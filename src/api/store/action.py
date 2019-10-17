from database.models import Action, UserProfile, Community, Media
from api.api_errors.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError
from api.utils.massenergize_response import MassenergizeResponse
import random

class ActionStore:
  def __init__(self):
    self.name = "Action Store/DB"

  def get_action_info(self, action_id) -> (dict, MassEnergizeAPIError):
    action = Action.objects.get(id=action_id)
    if not action:
      return None, InvalidResourceError()
    return action, None


  def list_actions(self, community_id) -> (list, MassEnergizeAPIError):
    actions = Action.objects.filter(community__id=community_id)
    if not actions:
      return [], None
    return actions, None


  def create_action(self, community_id, args) -> (dict, MassEnergizeAPIError):
    try:

      tags = args.pop('tags', [])
      vendors = args.pop('vendors', [])
      image = args.pop('image', None)
      new_action = Action.objects.create(**args)
      if community_id:
        community = Community.objects.get(id=community_id)
        new_action.community = community
      
      if image:
        media = Media.objects.create(name=f"{args['title']}-Action-Image", file=image)
        new_action.image = media
      
      #save so you set an id
      new_action.save()

      if tags:
        new_action.tags.set(tags)

      if vendors:
        new_action.vendors.set(vendors)
    
      new_action.save()
      return new_action, None

    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(e)

  def copy_action(self, action_id) -> (Action, MassEnergizeAPIError):
    try:
      #find the action
      action_to_copy = Action.objects.filter(id=action_id).first()
      if not action_to_copy:
        return None, InvalidResourceError()
      old_tags = action_to_copy.tags.all()
      new_action = action_to_copy
      new_action.pk = None
      new_action.title = action_to_copy.title + f' Copy {random.randint(1,10000)}'
      new_action.save()
      new_action.tags.set(old_tags)
      return new_action, None
    except Exception as e:
      return None, CustomMassenergizeError(str(e))


  def update_action(self, action_id, args) -> (dict, MassEnergizeAPIError):
    action = Action.objects.filter(id=action_id)
    if not action:
      return None, InvalidResourceError()
    action.update(**args)
    return action, None


  def delete_action(self, action_id) -> (Action, MassEnergizeAPIError):
    try:
      #find the action
      actions_to_delete = Action.objects.filter(id=action_id)
      actions_to_delete.update(is_deleted=True)
      if not actions_to_delete:
        return None, InvalidResourceError()
      return actions_to_delete.first(), None
    except Exception as e:
      return None, CustomMassenergizeError(str(e))

  def list_actions_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    actions = Action.objects.filter(community__id = community_id)
    return actions, None


  def list_actions_for_super_admin(self):
    try:
      actions = Action.objects.filter(is_deleted=False);
      return actions, None
    except Exception as e:
      return None, CustomMassenergizeError(str(e))