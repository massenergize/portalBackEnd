"""Handler file for all routes pertaining to events"""

from _main_.utils.route_handler import RouteHandler
from _main_.utils.common import get_request_contents, parse_list, parse_bool, check_length, parse_date, parse_int, parse_location
from api.services.event import EventService
from _main_.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function
from _main_.utils.context import Context
from _main_.utils.validator import Validator
from api.decorators import admins_only, super_admins_only, login_required


class EventHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.service = EventService()
    self.registerRoutes()

  def registerRoutes(self) -> None:
    self.add("/events.info", self.info) 
    self.add("/events.create", self.create)
    self.add("/events.add", self.create)
    self.add("/events.copy", self.copy)
    self.add("/events.list", self.list)
    self.add("/events.update", self.update)
    self.add("/events.delete", self.delete)
    self.add("/events.remove", self.delete)
    self.add("/events.rank", self.rank)
    self.add("/events.rsvp", self.rsvp)
    self.add("/events.rsvp.update", self.rsvp_update)
    self.add("/events.rsvp.remove", self.rsvp_remove)
    self.add("/events.todo", self.save_for_later)

    #admin routes
    self.add("/events.listForCommunityAdmin", self.community_admin_list)
    self.add("/events.listForSuperAdmin", self.super_admin_list)


  def info(self, request):
    context: Context = request.context
    args: dict = context.args
    
    self.validator.expect("event_id", int, is_required=True)
    args, err = self.validator.verify(args, strict=True)

    if err:
      return err

    event_info, err = self.service.get_event_info(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=event_info)


  @admins_only
  def copy(self, request):
    context: Context = request.context
    args: dict = context.args
    
    self.validator.expect("event_id", int, is_required=True)
    args, err = self.validator.verify(args, strict=True)

    if err:
      return err

    event_info, err = self.service.copy_event(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=event_info)


  @login_required
  def rsvp(self, request):
    context: Context = request.context
    args: dict = context.args
    
    self.validator.expect("event_id", int, is_required=True)
    args, err = self.validator.verify(args, strict=True)

    if err:
      return err

    event_info, err = self.service.rsvp(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=event_info)


  @login_required
  def rsvp_update(self, request) -> function:
    context: Context = request.context
    args: dict = context.args

    self.validator.expect("event_id", int, is_required=True)
    self.validator.expect("status", str, is_required=False)
    args, err = self.validator.verify(args, strict=True)

    if err:
      return err

    event_info, err = self.service.rsvp_update(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=event_info)


  @login_required
  def rsvp_remove(self, request):
    context: Context = request.context
    args: dict = context.args
    
    self.validator.expect("rsvp_id", int, is_required=True)
    args, err = self.validator.verify(args, strict=True)

    if err:
      return err

    event_info, err = self.service.rsvp_remove(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=event_info)


  @login_required
  def save_for_later(self, request):
    context: Context = request.context
    args: dict = context.args

    self.validator.expect("event_id", int, is_required=True)
    args, err = self.validator.verify(args, strict=True)

    if err:
      return err

    event_info, err = self.service.get_event_info(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=event_info)

  # TODO implement validator
  @admins_only
  def create(self, request):
    context: Context = request.context
    args: dict = context.args

    self.validator.expect('name', str, is_required=True, options={"min_length":5, "max_length":100})
    self.validator.expect('tags', list)
    self.validator.expect('is_global', bool)
    self.validator.expect('archive', bool)
    self.validator.expect('is_published', bool)
    self.validator.expect('have_address', bool)
    self.validator.expect('location', 'location')
    args, err = self.validator.verify(args)

    if err:
      return err

    event_info, err = self.service.create_event(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=event_info)


  def list(self, request):
    context: Context = request.context
    args: dict = context.args

    self.validator.expect("community_id", is_required=False)
    self.validator.expect("subdomain", is_required=False)
    self.validator.expect("user_id", is_required=False)
    args, err = self.validator.verify(args, strict=True)

    if err:
      return err

    event_info, err = self.service.list_events(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=event_info)

  # TODO implement validator
  @admins_only
  def update(self, request):
    context: Context = request.context
    args: dict = context.args

    self.validator.expect('event_id', int, is_required=True)
    self.validator.expect('name', str, is_required=True, options={"min_length":5, "max_length":100})
    self.validator.expect('tags', list)
    self.validator.expect('is_global', bool)
    self.validator.expect('archive', bool)
    self.validator.expect('is_published', bool)
    self.validator.expect('have_address', bool)
    self.validator.expect('location', 'location')
    args, err = self.validator.verify(args)

    if err:
      return err

    event_info, err = self.service.update_event(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=event_info)

  @admins_only
  def rank(self, request):
    context: Context = request.context
    args: dict = context.args

    self.validator.expect('id', int, is_required=True)
    self.validator.expect('rank', int, is_required=True)
    self.validator.rename('event_id', 'id')

    args, err = self.validator.verify(args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)

    event_info, err = self.service.rank_event(args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=event_info)


  @admins_only
  def delete(self, request):
    context: Context = request.context
    args: dict = context.args
    event_id = args.get("event_id", None)
    event_info, err = self.service.delete_event(context, event_id)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=event_info)


  @admins_only
  def community_admin_list(self, request):
    context: Context = request.context
    args: dict = context.args

    self.validator.expect("community_id", int, is_required=False)
    args, err = self.validator.verify(args)
    if err:
      return err

    events, err = self.service.list_events_for_community_admin(context, args)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=events)


  @super_admins_only
  def super_admin_list(self, request):
    context: Context = request.context
    events, err = self.service.list_events_for_super_admin(context)
    if err:
      return MassenergizeResponse(error=str(err), status=err.status)
    return MassenergizeResponse(data=events)
