from database.models import Team, UserProfile, Media, Community, TeamMember, CommunityAdminGroup
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError, NotAuthorizedError
from _main_.utils.massenergize_response import MassenergizeResponse
from django.utils.text import slugify
from _main_.utils.context import Context
from _main_.utils.constants import COMMUNITY_URL_ROOT, ADMIN_URL_ROOT
from _main_.utils.common import is_value
from .utils import get_community_or_die, get_user_or_die, get_admin_communities
from database.models import Team, UserProfile
from sentry_sdk import capture_message
from _main_.utils.emailer.send_email import send_massenergize_email

def can_set_parent(parent, this_team=None):
  if parent.parent:
    return False
  if this_team and Team.objects.filter(parent=this_team, is_deleted=False).exists():
    return False
  return True

def get_team_users(team):
  team_users = [tm.user for tm in
                  TeamMember.objects.filter(team=team, is_deleted=False).select_related('user')]
  if team.parent:
    return team_users
  else:
    child_teams = Team.objects.filter(parent=team, is_deleted=False, is_published=True)
    child_team_users = [tm.user for tm in
                  TeamMember.objects.filter(team__in=child_teams, is_deleted=False).select_related('user')]
    return set().union(team_users, child_team_users)

class TeamStore:
  def __init__(self):
    self.name = "Team Store/DB"

  def get_team_info(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    try:
      team_id = args.get("id", None)
      team = Team.objects.filter(id=team_id).first()
      if not team:
        return None, InvalidResourceError()

      userOnTeam = False 
      if context.user_id:    # None for anonymous usage
        user = UserProfile.objects.get(id=context.user_id)
        userOnTeam = TeamMember.objects.filter(team=team, user=user).exists()
 
      #TODO: untested
      if not team.is_published and not (context.user_is_admin() or userOnTeam):
        return None, CustomMassenergizeError("Cannot access team until it is approved")
      return team, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def get_team_admins(self, context, team_id):
    try:
      if not team_id:
        return None, CustomMassenergizeError("provide_team_id")
      team_admins = TeamMember.objects.filter(is_admin=True, team__id=team_id, is_deleted=False)
      team_admins = [a.user for a in team_admins if a.user]
      return team_admins, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

      
  def list_teams(self, context: Context, args) -> (list, MassEnergizeAPIError):
    try:
      community = get_community_or_die(context, args)
      user = get_user_or_die(context, args)

      if community:
        teams = Team.objects.filter(community=community, is_published=True, is_deleted=False)
      elif user:
        teams = user.team_set.all()
      return teams, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def team_stats(self, context: Context, args) -> (list, MassEnergizeAPIError):
    try:
      community = get_community_or_die(context, args)
      teams = Team.objects.filter(community=community, is_deleted=False)

      # show unpublished teams only in sandbox.
      # TODO: Better solution would be to show also for the user who created the team, but more complicated
      if not context.is_sandbox:
        teams = teams.filter(is_published=True)

      ans = []
      for team in teams:
        res = {"members": 0, "households": 0, "actions": 0, "actions_completed": 0, "actions_todo": 0, "carbon_footprint_reduction": 0}
        res["team"] = team.simple_json()
   
        users = get_team_users(team)
        res["members"] = len(users)
        for user in users:
          res["households"] += user.real_estate_units.count()
          actions = user.useractionrel_set.all()
          res["actions"] += len(actions)
          done_actions = actions.filter(status="DONE").prefetch_related('action__calculator_action')
          res["actions_completed"] += done_actions.count()
          res["actions_todo"] += actions.filter(status="TODO").count()
          for done_action in done_actions:
            if done_action.action and done_action.action.calculator_action:
              res["carbon_footprint_reduction"] += done_action.action.calculator_action.average_points

        ans.append(res)

      return ans, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def create_team(self, context:Context, args) -> (dict, MassEnergizeAPIError):
    team = None
    try:
      # generally a Team will have one community, but in principle it could span multiple.  If it 
      community_id = args.pop('community_id', None)
      community_ids = args.pop('community_ids', None)   # in case of a team spanning multiple communities
      logo_file = args.pop('logo', None)
      image_files = args.pop('pictures', None)
      video = args.pop('video', None)
      parent_id = args.pop('parent_id', None)
      args.pop('undefined', None)

      admin_emails = args.pop('admin_emails', [])
      
      verified_admins = []
      #verify that provided emails are valid user
      for email in admin_emails:
        admin =  UserProfile.objects.filter(email=email).first()
        if admin:
          verified_admins.append(admin)
        else:
          return None, CustomMassenergizeError(f"Email: {email} is not registered with us")
      
      if not verified_admins:
        return None, CustomMassenergizeError(f"Please provide at least one admin's email")

      if community_id:
        community = Community.objects.filter(pk=community_id).first()
        if not community:
          return None, CustomMassenergizeError("Please provide a valid community")
        args["community"] = community
        community_list = None
      elif community_ids:       # the case of multiple communities
        community_list = []
        for community_id in community_ids:
          community = Community.objects.filter(pk=community_id).first()
          if not community:
            return None, CustomMassenergizeError("Please provide a valid community in the list")
          community_list.append(community)
      else:
        return None, CustomMassenergizeError("Please provide a community")
      
      team, _ = Team.objects.get_or_create(**args)

      # add multiple communities if that is the case (generally not)
      if community_list:
        for community in community_list:
          team.community.add(community)

      # for the case of a sub-team, record the parent
      if parent_id:
        parent = Team.objects.filter(pk=parent_id).first()
        if parent and can_set_parent(parent):
          team.parent = parent
        else:
          return None, CustomMassenergizeError("Cannot set parent team")

      if logo_file:
        logo = Media.objects.create(file=logo_file, name=f"{slugify(team.name)}-TeamLogo")
        logo.save()
        team.logo = logo

      # TODO: this code does will not make sense when there are multiple communities for the team...
      # TODO: create a rich email template for this?
      
      # Wnen team initially created, it is not visible until reviewed by community admin
      is_published = False
      team.is_published = is_published
      if not is_published:
        cadmins = CommunityAdminGroup.objects.filter(community__id=community_id).first().members.all()
        message = "A team has requested creation in your community. Visit the link below to view their information and if it is satisfactory, check the approval box and update the team.\n\n%s" % ("%s/admin/edit/%i/team" %
          (ADMIN_URL_ROOT, team.id))

        for cadmin in cadmins:
          send_massenergize_email(subject="New team awaiting approval",
                                msg=message, to=cadmin.email)
      team.save()
      for admin in verified_admins:
        teamMember, _ = TeamMember.objects.get_or_create(team=team,user=admin)
        teamMember.is_admin = True
        teamMember.save()

      return team, None
    except Exception as e:
      capture_message(str(e), level="error")
      if team:
        team.delete()
      return None, CustomMassenergizeError(str(e))


  def update_team(self, context, args) -> (dict, MassEnergizeAPIError):
    try:
      team_id = args.get('id', None)
      community_id = args.pop('community_id', None)
      if community_id:
        community = Community.objects.filter(pk=community_id).first()
        subdomain = community.subdomain
      else:
        subdomain = "your_community"

      logo = args.pop('logo', None)
      parent_id = args.pop('parent_id', None)
      is_published = args.pop('is_published', False)
        
      team = Team.objects.filter(id=team_id)

      # to update Team, need to be super_admin, community_admin of that community, or a team_admin
      allowed = False
      if context.user_is_super_admin:
        allowed = True
      elif context.user_is_community_admin:
        community = team.first().community
        admin_communities, err = get_admin_communities(context)
        if community in admin_communities:
          allowed = True
      else:
        # user has to be on the team admin list
        teamMembers = TeamMember.objects.filter(team=team.first())
        for teamMember in teamMembers:
          teamMember_id = str(teamMember.user.id)
          if teamMember_id == context.user_id and teamMember.is_admin:
            allowed = True
            break

      if not allowed:
        return None, NotAuthorizedError()

      team.update(**args)
      team = team.first()

      # TODO: create a rich email template for this?
      # TODO: only allow a cadmin or super admin to change this particular field?
      if is_published and not team.is_published:
        team.is_published = True
        team_admins = TeamMember.objects.filter(team=team, is_admin=True).select_related('user')
        # fix the broken URL in this message, needs to have community nam
        message = "Your team %s has now been approved by a Community Admin and is viewable to anyone on the MassEnergize portal. See it here:\n\n%s" % (team.name, ("%s/%s/teams/%i") % (COMMUNITY_URL_ROOT, subdomain, team.id))
        for team_admin in team_admins:
          send_massenergize_email(subject="Your team has been approved",
                                msg=message, to=team_admin.user.email)
      else:
        # this is how teams can get be made not live
        team.is_published = is_published

      if community_id:
        community = Community.objects.filter(pk=community_id).first()
        if community:
            team.community = community          

      if parent_id:
          team.parent = None
          parent = Team.objects.filter(pk=parent_id).first()
          if parent and can_set_parent(parent, this_team=team):
            team.parent = parent
        
      if logo:
          # if existing logo, the string length is around 300 characters
          # If a new logo updated, this will be the length of the file, much larger than that       
          new_logo = len(logo) > 1000
          if new_logo:
            logo = Media.objects.create(file=logo, name=f"{slugify(team.name)}-TeamLogo")
            logo.save()
            team.logo = logo
          else: 
            team.logo = None 

      team.save()
      return team, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)
    

  def delete_team(self, args) -> (dict, MassEnergizeAPIError):
    try:
      team_id = args["id"]
      teams = Team.objects.filter(id=team_id)
      if not teams:
        return None, InvalidResourceError()


      # team.members deprecated.  Delete TeamMembers separate step
      team = teams.first()
      members = TeamMember.objects.filter(team=team)
      members.delete()
      team.delete()  # or should that be team.delete()?

      return teams.first(), None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def join_team(self, args) -> (Team, MassEnergizeAPIError):
    try:
      team_id = args.get("id", None)
      user_id = args.get("user_id", None)

      team = Team.objects.get(id=team_id)
      user = UserProfile.objects.get(id=user_id)
      teamMember, created = TeamMember.objects.get_or_create(team=team, user=user)
      if created:
        teamMember.save()

      return team, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(str(e))

  def leave_team(self, args) -> (Team, MassEnergizeAPIError):
    try:
      team_id = args.get("id", None)
      user_id = args.get("user_id", None)
      team = Team.objects.get(id=team_id)
      user = UserProfile.objects.get(id=user_id)
      teamMember = TeamMember.objects.filter(team=team, user=user)
      if teamMember:
        teamMember.delete()
      else:
        return None, CustomMassenergizeError("User is not in that team")

      return team, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(str(e))

  def add_team_member(self, args) -> (Team, MassEnergizeAPIError):
    try:
      team_id = args.get("id", None)
      user_id = args.get("user_id", None)

      team = Team.objects.get(id=team_id)
      user = UserProfile.objects.get(id=user_id)
      teamMember, created = TeamMember.objects.get_or_create(team=team, user=user)      
      if created:
        teamMember.save()
      
      return team, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

  def remove_team_member(self, args) -> (Team, MassEnergizeAPIError):
    try:
      team_id = args.get('id', None)
      user_id = args.get('user_id', None)
      team = Team.objects.get(id=team_id)
      user = UserProfile.objects.get(id=user_id)
      team_member = TeamMember.objects.filter(team__id=team_id, user=user)
      if team_member.count() > 0:
        team_member.delete()
      return team, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def members(self, context: Context, args) -> (Team, MassEnergizeAPIError):
    try:
      if not context.user_is_admin():
        return None, NotAuthorizedError()
      team_id = args.get('team_id', None)
      if not team_id:
        return [], CustomMassenergizeError('Please provide a valid team_id')

      members = TeamMember.objects.filter(is_deleted=False, team__id=team_id)
      return members, None
    except Exception:
      return None, InvalidResourceError()

# shouldnt return user id (potential security issue?)
  def members_preferred_names(self, context: Context, args) -> (Team, MassEnergizeAPIError):
    try:
      team_id = args.get('team_id', None)
      if not team_id:
        return [], CustomMassenergizeError('Please provide a valid team_id')

      team = Team.objects.filter(id=team_id).first()
      users = get_team_users(team)
      res = []
      for user in users:
        member = TeamMember.objects.filter(user=user, team=team).first()
        member_obj = {"id": None, "user_id": str(user.id), "preferred_name": user.preferred_name, "is_admin": False}
        if member:
          member_obj['id'] = member.id
          member_obj['is_admin'] = member.is_admin
        res.append(member_obj)

      return res, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, InvalidResourceError()


  def list_teams_for_community_admin(self, context: Context, args) -> (list, MassEnergizeAPIError):
    try:
      if context.user_is_super_admin:
        return self.list_teams_for_super_admin(context)

      community_id = args.pop('community_id', None)
      if not is_value(community_id):
        user = UserProfile.objects.get(pk=context.user_id)
        admin_groups = user.communityadmingroup_set.all()
        comm_ids = [ag.community.id for ag in admin_groups]
        teams = Team.objects.filter(community__id__in = comm_ids, is_deleted=False).select_related('logo', 'community')
        return teams, None

      teams = Team.objects.filter(community__id = community_id, is_deleted=False).select_related('logo', 'community')
      
      return teams, None

    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

  def list_teams_for_super_admin(self, context: Context):
    try:
      if not context.user_is_super_admin:
        return None, NotAuthorizedError()
      teams = Team.objects.filter(is_deleted=False).select_related('logo', 'community')
      return teams, None

    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(str(e))
