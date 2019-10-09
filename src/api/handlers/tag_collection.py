"""Handler file for all routes pertaining to tag_collections"""

from api.utils.route_handler import RouteHandler
from api.utils.common import get_request_contents
from api.services.tag_collection import TagCollectionService
from api.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function

#TODO: install middleware to catch authz violations
#TODO: add logger

class TagCollectionHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.tag_collection = TagCollectionService()
    self.registerRoutes()

  def registerRoutes(self) -> None:
    self.add("/tag_collections.info", self.info()) 
    self.add("/tag_collections.create", self.create())
    self.add("/tag_collections.add", self.create())
    self.add("/tag_collections.list", self.list())
    self.add("/tag_collections.update", self.update())
    self.add("/tag_collections.delete", self.delete())
    self.add("/tag_collections.remove", self.delete())

    #admin routes
    self.add("/tag_collections.listForCommunityAdmin", self.community_admin_list())
    self.add("/tag_collections.listForSuperAdmin", self.super_admin_list())


  def info(self) -> function:
    def tag_collection_info_view(request) -> None: 
      args = get_request_contents(request)
      tag_collection_info, err = self.tag_collection.info(args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=tag_collection_info)
    return tag_collection_info_view


  def create(self) -> function:
    def create_tag_collection_view(request) -> None: 
      args = get_request_contents(request)
      tag_collection_info, err = self.tag_collection.create(args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=tag_collection_info)
    return create_tag_collection_view


  def list(self) -> function:
    def list_tag_collection_view(request) -> None: 
      args = get_request_contents(request)
      community_id = args["community__id"]
      user_id = args["user_id"]
      tag_collection_info, err = self.tag_collection.list_tag_collections(community_id, user_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=tag_collection_info)
    return list_tag_collection_view


  def update(self) -> function:
    def update_tag_collection_view(request) -> None: 
      args = get_request_contents(request)
      tag_collection_info, err = self.tag_collection.update_tag_collection(args[id], args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=tag_collection_info)
    return update_tag_collection_view


  def delete(self) -> function:
    def delete_tag_collection_view(request) -> None: 
      args = get_request_contents(request)
      tag_collection_id = args[id]
      tag_collection_info, err = self.tag_collection.delete_tag_collection(args[id])
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=tag_collection_info)
    return delete_tag_collection_view


  def community_admin_list(self) -> function:
    def community_admin_list_view(request) -> None: 
      args = get_request_contents(request)
      community_id = args.get("community__id")
      tag_collections, err = self.tag_collection.list_tag_collections_for_community_admin(community_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=tag_collections)
    return community_admin_list_view


  def super_admin_list(self) -> function:
    def super_admin_list_view(request) -> None: 
      args = get_request_contents(request)
      tag_collections, err = self.tag_collection.list_tag_collections_for_super_admin()
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=tag_collections)
    return super_admin_list_view