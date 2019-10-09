"""Handler file for all routes pertaining to policies"""

from api.utils.route_handler import RouteHandler
from api.utils.common import get_request_contents
from api.services.policy import PolicyService
from api.utils.massenergize_response import MassenergizeResponse
from types import FunctionType as function

#TODO: install middleware to catch authz violations
#TODO: add logger

class PolicyHandler(RouteHandler):

  def __init__(self):
    super().__init__()
    self.policy = PolicyService()
    self.registerRoutes()

  def registerRoutes(self) -> None:
    self.add("/policies.info", self.info()) 
    self.add("/policies.create", self.create())
    self.add("/policies.add", self.create())
    self.add("/policies.list", self.list())
    self.add("/policies.update", self.update())
    self.add("/policies.delete", self.delete())
    self.add("/policies.remove", self.delete())

    #admin routes
    self.add("/policies.listForCommunityAdmin", self.community_admin_list())
    self.add("/policies.listForSuperAdmin", self.super_admin_list())


  def info(self) -> function:
    def policy_info_view(request) -> None: 
      args = get_request_contents(request)
      policy_info, err = self.policy.info(args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=policy_info)
    return policy_info_view


  def create(self) -> function:
    def create_policy_view(request) -> None: 
      args = get_request_contents(request)
      policy_info, err = self.policy.create(args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=policy_info)
    return create_policy_view


  def list(self) -> function:
    def list_policy_view(request) -> None: 
      args = get_request_contents(request)
      community_id = args["community__id"]
      user_id = args["user_id"]
      policy_info, err = self.policy.list_policies(community_id, user_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=policy_info)
    return list_policy_view


  def update(self) -> function:
    def update_policy_view(request) -> None: 
      args = get_request_contents(request)
      policy_info, err = self.policy.update_policy(args[id], args)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=policy_info)
    return update_policy_view


  def delete(self) -> function:
    def delete_policy_view(request) -> None: 
      args = get_request_contents(request)
      policy_id = args[id]
      policy_info, err = self.policy.delete_policy(args[id])
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=policy_info)
    return delete_policy_view


  def community_admin_list(self) -> function:
    def community_admin_list_view(request) -> None: 
      args = get_request_contents(request)
      community_id = args.get("community__id")
      policies, err = self.policy.list_policies_for_community_admin(community_id)
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=policies)
    return community_admin_list_view


  def super_admin_list(self) -> function:
    def super_admin_list_view(request) -> None: 
      args = get_request_contents(request)
      policies, err = self.policy.list_policies_for_super_admin()
      if err:
        return MassenergizeResponse(error=str(err), status=err.status)
      return MassenergizeResponse(data=policies)
    return super_admin_list_view