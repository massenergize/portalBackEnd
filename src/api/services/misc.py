from _main_.utils.massenergize_errors import MassEnergizeAPIError, CustomMassenergizeError
from _main_.utils.massenergize_response import MassenergizeResponse
from _main_.utils.common import serialize, serialize_all
from api.store.misc import MiscellaneousStore
from _main_.utils.context import Context


class MiscellaneousService:
  """
  Service Layer for all the goals
  """

  def __init__(self):
    self.store =  MiscellaneousStore()

  
  def navigation_menu_list(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    main_menu_items, err = self.store.navigation_menu_list(context, args)
    if err:
      return None, err
    return serialize_all(main_menu_items), None
  
  def backfill(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    result, err = self.store.backfill(context, args)
    if err:
      return None, err
    return result, None

  def create_carbon_equivalency(self, context, args) -> (dict, MassEnergizeAPIError):
    carbon_data, err = self.store.create_carbon_equivalency(context, args)
    if err:
      return None, err
    return carbon_data, None

  def update_carbon_equivalency(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    carbon_data, err = self.store.update_carbon_equivalency(context, args)
    if err:
      return None, err
    return carbon_data, None
  
  def get_carbon_equivalencies(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    carbon_data, err = self.store.get_carbon_equivalencies(context, args)
    if err:
      return None, err
    return serialize_all(carbon_data), None

  def delete_carbon_equivalency(self, context: Context, args) -> (dict, MassEnergizeAPIError):
    carbon_data, err = self.store.delete_carbon_equivalency(context, args)
    if err:
      return None, err
    return carbon_data, None