from database.models import Event, RecurringEventException, UserProfile, EventAttendee, Media, Community
from _main_.utils.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError, NotAuthorizedError
from _main_.utils.massenergize_response import MassenergizeResponse
from django.db.models import Q
from _main_.utils.context import Context
from sentry_sdk import capture_message
from .utils import get_user_or_die
import datetime
from datetime import timedelta
import calendar
from math import ceil

class EventStore:
  def __init__(self):
    self.name = "Event Store/DB"

  def get_event_info(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    try:
      event_id = args.pop("event_id")

      events_selected = Event.objects.select_related('image', 'community').prefetch_related('tags', 'invited_communities').filter(id=event_id)
      event = events_selected.first()
      if not event:
        return None, InvalidResourceError()
      return event, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

  def copy_event(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    try:
      event_id = args.pop("event_id")

      events_selected = Event.objects.select_related('image', 'community').prefetch_related('tags', 'invited_communities').filter(id=event_id)
      event_to_copy: Event = events_selected.first()
      if not event_to_copy:
        return None, InvalidResourceError()
      
      old_tags = event_to_copy.tags.all()
      event_to_copy.pk = None
      new_event = event_to_copy 
      new_event.name = event_to_copy.name + "-Copy"
      new_event.is_published=False
      new_event.is_global = False
      new_event.start_date_and_time = event_to_copy.start_date_and_time
      new_event.end_date_and_time = event_to_copy.end_date_and_time
      new_event.description = event_to_copy.description
      new_event.featured_summary = event_to_copy.featured_summary
      new_event.location = event_to_copy.location
      if event_to_copy.is_recurring:
        new_event.recurring_details = event_to_copy.recurring_details
      new_event.save()

      #copy tags over
      for t in old_tags:
        new_event.tags.add(t)

      return new_event, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

  def list_recurring_event_exceptions(self, context: Context, args) -> (list, MassEnergizeAPIError):
    event_id = args.pop("event_id", None)
    corresponding_event: Event = Event.objects.filter(id=event_id).first()
    e = RecurringEventException.objects.filter(event=corresponding_event)
    
    return e, None


  def list_events(self, context: Context, args) -> (list, MassEnergizeAPIError):
    community_id = args.pop("community_id", None)
    subdomain = args.pop("subdomain", None)
    user_id = args.pop("user_id", None)

    if community_id:
      #TODO: also account for communities who are added as invited_communities
      query =Q(community__id=community_id)
      events = Event.objects.select_related('image', 'community').prefetch_related('tags', 'invited_communities').filter(query)
    elif subdomain:
      query =  Q(community__subdomain=subdomain)
      events = Event.objects.select_related('image', 'community').prefetch_related('tags', 'invited_communities').filter(query)

    elif user_id:
      events = EventAttendee.objects.filter(attendee=user_id)
    else:
      events = []
    
    if not context.is_sandbox and events:
      events = events.filter(is_published=True)
  
    return events, None


  def create_event(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    print(args)
    try:
      image = args.pop('image', None)
      tags = args.pop('tags', [])
      community = args.pop("community_id", None)
      is_recurring  = args.pop('is_recurring', False)
      if is_recurring == "false" or is_recurring == "":
        recurring = False
      else: recurring = True
      recurring_type = args.pop('recurring_type', None)
      separation_count = args.pop('separation_count', None)
      separation_count = int(separation_count)
    
      day_of_week = args.pop('day_of_week', None)
      start_date_and_time = args.get('start_date_and_time', None)
      end_date_and_time = args.get('end_date_and_time', None)
      week_of_month = args.pop("week_of_month", None)
      if recurring_type != "month":
        week_of_month = None
      have_address = args.pop('have_address', False)
      # since this gets passed in as an English word, we need to convert it to an integer first
      converter = {"first":1, "second":2, "third":3, "fourth":4}
          
      if not have_address:
        args['location'] = None

      if community:
        community = Community.objects.get(pk=community)
        if not community:
          return None, CustomMassenergizeError("Please provide a valid community_id")
      # check that the event's start date coincides with the recurrence pattern if it is listed as recurring
      if recurring  and start_date_and_time:
        # extract month, day and year from start_date_and_time
        date = start_date_and_time[0:10:1].split('-')
        day = datetime.datetime(int(date[0]), int(date[1]), int(date[2]))
        # check if weekday matches the start_date_and_time
        if calendar.day_name[day.weekday()] != day_of_week:
          return None, CustomMassenergizeError("Starting date and time does not match the recurrence pattern for the event")
        # if necessary, check if week of month matches the start_date...
        if week_of_month:
          # let's say the date passed in represents the Nth occurence of a particular weekday in the month 
          # we find N
          # get the first instance of the same weekday in the month
          obj = calendar.Calendar()
          date_of_first_weekday = 1
          for d in obj.itermonthdates(int(day.year), int(day.month)):
            if int(d.day >= 8):
              continue
            d1 = datetime.datetime(int(d.year), int(d.month), int(d.day))
            if calendar.day_name[d1.weekday()] == day_of_week:
              date_of_first_weekday = int(d1.day)
              print(date_of_first_weekday)
              diff = day.day - date_of_first_weekday
              if converter[week_of_month] - 1 != diff/7:
                return None, CustomMassenergizeError("Starting date and time does not match the recurrence pattern for the event")
            
        end_date = end_date_and_time[0:10:1].split('-')
        end_day = datetime.datetime(int(end_date[0]), int(end_date[1]), int(end_date[2]))
        # TODO: check that starting date and time is earlier than ending date and time (need to edit substring thingy)

        # check that if the event does not go longer than a day (recurring events cannot go longer than 1 day)
        if day.date() != end_day.date():
          return None, CustomMassenergizeError("Recurring events must only last 1 day. Make sure your starting date and ending date are the same")
      new_event: Event = Event.objects.create(**args)
      if community:
        new_event.community = community

      if image:
        media = Media.objects.create(file=image, name=f"ImageFor{args.get('name', '')}Event")
        new_event.image = media


      if recurring and day_of_week: 
        new_event.is_recurring = True
        new_event.recurring_details = {
          "recurring_type": recurring_type, 
          "separation_count": separation_count, 
          "day_of_week": day_of_week, 
          "week_of_month": week_of_month
        } 
      

      new_event.save()
      weekdays = {"Monday":0, "Tuesday":1, "Wednesday":2, "Thursday":3, "Friday":4, "Saturday":5, "Sunday":6}
      
      if recurring_type == "week":
        if separation_count == 1:
          today = datetime.datetime.today()
          diff = weekdays[day_of_week] - today.weekday()
          if diff < 0: diff += 7
          change = timedelta(days=diff)
          upcoming_date = today + change
          print(upcoming_date)
          # TODO: create datetime for start_date_and_time, update
        elif separation_count != 1:
          # get the occurence of the last event
          # start_date_and_time stores the UPCOMING EVENT instance; 
          # in this case, it is not updated, so we use it as our old event instance so we can update it
          last = new_event.start_date_and_time[0:10:1].split('-')
          last_date = datetime.datetime(int(last[0]), int(last[1]), int(last[2]))
          diff = weekdays[day_of_week] - last_date.weekday()
          if diff < 0: diff += 7
          for i in range(separation_count - 1):
            diff += 7
          change = timedelta(days = diff)
          upcoming_date = last_date + change
          print(str(upcoming_date))
          # TODO: create datetime for start_date_and_time, update
      elif recurring_type == "month":
        print('month branch')
        if separation_count == 1:
          # get next (week_of_month) (day_of_week), whether that's this month or next monthu
          # check if today is past this month's (week_of_month) (day_of_week)
          # get the first week of the current month
          d = datetime.datetime.now()
          obj = calendar.Calendar()
          date_of_first_weekday = 0
          for day in obj.itermonthdates(int(d.year), int(d.month)):
            if int(day.day) >= 8:
              continue
            d1 = datetime.datetime(int(d.year), int(d.month), int(day.day))
            print(calendar.day_name[d1.weekday()])
            print(day_of_week)
            if calendar.day_name[d1.weekday()] == day_of_week:
              print('printing weekday')
              print(d1.weekday)
              date_of_first_weekday = int(day.day)
              print('date of first weekday')
              print(date_of_first_weekday)
              break
          # we have obtained the date of the first (day_of_week) of the month
          upcoming_date = date_of_first_weekday + ((converter[week_of_month] - 1)*7)
          print(upcoming_date)
          # if the event has already passed this month, we get the next month
          if (upcoming_date < d.day):
            change = timedelta(32)
            next_month = d + change
            # get the correct date for next month
            for day in obj.itermonthdates(int(next_month.year), (int(next_month.month))):
              if int(day.day >= 8):
                continue
              d2 = datetime.datetime(int(day.year), int(day.month) + 1, int(day.day))
              if weekdays[d2.weekday()] == day_of_week:
                upcoming_date = int(day.day)
                break
                # we have obtained the date of the first (day_of_week) of the month
              upcoming_date += ((converter[week_of_month] - 1)*7)
              print(upcoming_date)
        elif separation_count != 1:
          # assumes that there is a cycle of less than (separation_count) months before start_date... is updated
          last = new_event.start_date_and_time[0:10:1].split('-')
          last_date = datetime.datetime(int(last[0]), int(last[1]), int(last[2]))
          # use timedelta to get the new month
          change = timedelta((separation_count * 31) + 1)
          new_month = last_date + change
          # find the corresponding ith day of the jth month
          obj = calendar.Calendar()
          date_of_first_weekday = 0
          for day in obj.itermonthdates(int(new_month.year), int(new_month.month)):
            if int(day.day) >= 8:
              continue
            d1 = datetime.datetime(int(day.year), int(day.month), int(day.day))
            print(calendar.day_name[d1.weekday()])
            print(day_of_week)
            if calendar.day_name[d1.weekday()] == day_of_week:
              print('printing weekday')
              print(d1.weekday)
              date_of_first_weekday = int(day.day)
              print('date of first weekday')
              print(date_of_first_weekday)
              break
          # we have obtained the date of the first (day_of_week) of the month
          upcoming_date = date_of_first_weekday + ((converter[week_of_month] - 1)*7)
          print(str(new_month.month) +" " + str(upcoming_date))
      if tags:
        new_event.tags.set(tags)

      return new_event, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

  def update_event(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    try:
      event_id = args.pop('event_id', None)
      image = args.pop('image', None)
      tags = args.pop('tags', [])
      recurring  = args.pop('is_recurring', False)
      start_date_and_time = args.pop('start_date_and_time', None)
      end_date_and_time = args.pop('end_date_and_time', None)
      recurring_type = args.pop('recurring_type', None)
      separation_count = args.pop('separation_count', None)
      separation_count = int(separation_count)
      day_of_week = args.pop('day_of_week', None)
      week_of_month = args.pop("week_of_month", None)
      if recurring_type != "month":
        week_of_month = None
      upcoming_is_cancelled = args.pop("upcoming_is_cancelled", None)
      upcoming_is_rescheduled = args.pop('upcoming_is_rescheduled', None)

      events = Event.objects.filter(id=event_id)

      have_address = args.pop('have_address', False)
      if not have_address:
        args['location'] = None

      community = args.pop("community_id", None)
      if community:
        community = Community.objects.filter(pk=community).first()

      event: Event = events.first()
      event.is_recurring = recurring
      event.start_date_and_time = start_date_and_time
      event.end_date_and_time = end_date_and_time
      if not event:
        return None, CustomMassenergizeError(f"No event with id: {event_id}")

      if image:
        media = Media.objects.create(file=image, name=f"ImageFor{args.get('name', '')}Event")
        event.image = media
      
      if community:
        event.community = community
      else:
        event.community = None
      
      if recurring and day_of_week: 
        event.is_recurring = True
        event.recurring_details = {
          "recurring_type": recurring_type, 
          "separation_count": separation_count, 
          "day_of_week": day_of_week, 
          "week_of_month": week_of_month
        } 
      event.save()
      weekdays = {"Monday":0, "Tuesday":1, "Wednesday":2, "Thursday":3, "Friday":4, "Saturday":5, "Sunday":6}
      converter = {"first":1, "second":2, "third":3, "fourth":4}
      if recurring_type == "week":
        if separation_count == 1:
          today = datetime.datetime.today()
          diff = weekdays[day_of_week] - today.weekday()
          if diff < 0: diff += 7
          change = timedelta(days=diff)
          upcoming_date = today + change
          print(upcoming_date)
          # TODO: create datetime for start_date_and_time, update
        elif separation_count != 1:
          # get the occurence of the last event
          # start_date_and_time stores the UPCOMING EVENT instance; 
          # in this case, it is not updated, so we use it as our old event instance so we can update it
          last = event.start_date_and_time[0:10:1].split('-')
          last_date = datetime.datetime(int(last[0]), int(last[1]), int(last[2]))
          diff = weekdays[day_of_week] - last_date.weekday()
          if diff < 0: diff += 7
          for i in range(separation_count - 1):
            diff += 7
          change = timedelta(days = diff)
          upcoming_date = last_date + change
          print(str(upcoming_date))
          # TODO: create datetime for start_date_and_time, update
      elif recurring_type == "month":
        print('month branch')
        if separation_count == 1:
          # get next (week_of_month) (day_of_week), whether that's this month or next monthu
          # check if today is past this month's (week_of_month) (day_of_week)
          # get the first week of the current month
          d = datetime.datetime.now()
          obj = calendar.Calendar()
          date_of_first_weekday = 0
          for day in obj.itermonthdates(int(d.year), int(d.month)):
            if int(day.day) >= 8:
              continue
            d1 = datetime.datetime(int(d.year), int(d.month), int(day.day))
            print(calendar.day_name[d1.weekday()])
            print(day_of_week)
            if calendar.day_name[d1.weekday()] == day_of_week:
              print('printing weekday')
              print(d1.weekday)
              date_of_first_weekday = int(day.day)
              print('date of first weekday')
              print(date_of_first_weekday)
              break
          # we have obtained the date of the first (day_of_week) of the month
          upcoming_date = date_of_first_weekday + ((converter[week_of_month] - 1)*7)
          print(upcoming_date)
          # if the event has already passed this month, we get the next month
          if (upcoming_date < d.day):
            change = timedelta(32)
            next_month = d + change
            # get the correct date for next month
            for day in obj.itermonthdates(int(next_month.year), (int(next_month.month))):
              if int(day.day >= 8):
                continue
              d2 = datetime.datetime(int(day.year), int(day.month) + 1, int(day.day))
              if weekdays[d2.weekday()] == day_of_week:
                upcoming_date = int(day.day)
                break
                # we have obtained the date of the first (day_of_week) of the month
              upcoming_date += ((converter[week_of_month] - 1)*7)
              print(upcoming_date)
        elif separation_count != 1:
          # assumes that there is a cycle of less than (separation_count) months before start_date... is updated
          last = event.start_date_and_time[0:10:1].split('-')
          last_date = datetime.datetime(int(last[0]), int(last[1]), int(last[2]))
          # use timedelta to get the new month
          change = timedelta((separation_count * 31) + 1)
          new_month = last_date + change
          # find the corresponding ith day of the jth month
          obj = calendar.Calendar()
          date_of_first_weekday = 0
          for day in obj.itermonthdates(int(new_month.year), int(new_month.month)):
            if int(day.day) >= 8:
              continue
            d1 = datetime.datetime(int(day.year), int(day.month), int(day.day))
            print(calendar.day_name[d1.weekday()])
            print(day_of_week)
            if calendar.day_name[d1.weekday()] == day_of_week:
              print('printing weekday')
              print(d1.weekday)
              date_of_first_weekday = int(day.day)
              print('date of first weekday')
              print(date_of_first_weekday)
              break
          # we have obtained the date of the first (day_of_week) of the month
          upcoming_date = date_of_first_weekday + ((converter[week_of_month] - 1)*7)
          print(str(new_month.month) +" " + str(upcoming_date))
      
      # CAdmin is cancelling the upcoming event instance
      if upcoming_is_cancelled == 'true' or upcoming_is_cancelled == True:
        event.recurring_details["is_cancelled"] = True
      else:
        event.recurring_details["is_cancelled"] = False
      
      #CAdmin is rescheduling the upcoming event instance
      if upcoming_is_rescheduled == 'true' or upcoming_is_rescheduled == True:
        rescheduled_start = args.get('rescheduled_start_datetime', None)
        rescheduled_end = args.get('rescheduled_end_datetime', None)
        
        rescheduled_event = event
        rescheduled_event.id = None
        rescheduled_event.pk = None
        rescheduled_event.start_date_and_time = rescheduled_start
        rescheduled_event.end_date_and_time = rescheduled_end
        rescheduled_event.name = event.name + " (rescheduled)"
        rescheduled_event.save()
        rescheduled: RecurringEventException = RecurringEventException.objects.create(
          event = event,  
          former_time = event.start_date_and_time, 
          rescheduled_event = rescheduled_event
        )
        rescheduled.save()

      event.save()

      if tags:
        event.tags.set(tags)
      
      return event, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  
  def rank_event(self, args) -> (dict, MassEnergizeAPIError):
    try:
      id = args.get('id', None)
      rank = args.get('rank', None)
      if id and rank:

        events = Event.objects.filter(id=id)
        events.update(rank=rank)
        return events.first(), None
      else:
        raise Exception("Rank and ID not provided to events.rank")
      
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

  def delete_event(self, context: Context, event_id) -> (dict, MassEnergizeAPIError):
    try:
      events = Event.objects.filter(id=event_id)
      if not events:
        return None, InvalidResourceError()
      
      if len(events) > 1:
        return None, CustomMassenergizeError("Deleting multiple events not supported")

      events.delete()
      return events.first(), None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def list_events_for_community_admin(self, context: Context, args) -> (list, MassEnergizeAPIError):
    try:
      community_id = args.pop("community_id", None)

      if context.user_is_super_admin:
        return self.list_events_for_super_admin(context)

      elif not context.user_is_community_admin:
        return None, NotAuthorizedError()

      # community_id coming from admin portal is 'undefined'
      if not community_id or community_id=='undefined':
        user = UserProfile.objects.get(pk=context.user_id)
        admin_groups = user.communityadmingroup_set.all()
        comm_ids = [ag.community.id for ag in admin_groups]
        events = Event.objects.filter(Q(community__id__in = comm_ids) | Q(is_global=True), is_deleted=False).select_related('image', 'community').prefetch_related('tags')
        return events, None

      events = Event.objects.filter(Q(community__id = community_id) | Q(is_global=True), is_deleted=False).select_related('image', 'community').prefetch_related('tags')
      return events, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)


  def list_events_for_super_admin(self, context: Context):
    try:
      if not context.user_is_super_admin:
        return None, NotAuthorizedError()
      events = Event.objects.filter(is_deleted=False).select_related('image', 'community').prefetch_related('tags')
      return events, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(str(e))


  def rsvp(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    try:
      event_id = args.pop("event_id", None)
      args: dict = context.args
      user = get_user_or_die(context, args)
      event = Event.objects.filter(pk=event_id).first()
      if not event:
        return None, InvalidResourceError()

      event_attendee = EventAttendee.objects.create(
        event=event, attendee=user, status="RSVP")

      return event_attendee, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

  def rsvp_update(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    try:
      event_id = args.pop("event_id", None)
      status = args.pop("status", "SAVE")

      args: dict = context.args
      user = get_user_or_die(context, args)
      event = Event.objects.filter(pk=event_id).first()
      if not event:
        return None, InvalidResourceError()

      event_attendee = EventAttendee.objects.filter(
        event=event, attendee=user).update(status=status)

      return event_attendee, None
      
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)

  def rsvp_remove(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    try:
      rsvp_id = args.pop("rsvp_id", None)

      result = EventAttendee.objects.filter(pk=rsvp_id).delete()
      return result, None
    except Exception as e:
      capture_message(str(e), level="error")
      return None, CustomMassenergizeError(e)