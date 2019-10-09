from database.models import HomePageSettings, UserProfile
from api.api_errors.massenergize_errors import MassEnergizeAPIError, InvalidResourceError, ServerError, CustomMassenergizeError
from api.utils.massenergize_response import MassenergizeResponse

class HomePageSettingsStore:
  def __init__(self):
    self.name = "HomePageSettings Store/DB"

  def get_home_page_setting_info(self, home_page_setting_id) -> (dict, MassEnergizeAPIError):
    home_page_setting = HomePageSettings.objects.filter(id=home_page_setting_id)
    if not home_page_setting:
      return None, InvalidResourceError()
    return home_page_setting.full_json(), None


  def list_home_page_settings(self, community_id) -> (list, MassEnergizeAPIError):
    home_page_settings = HomePageSettings.objects.filter(community__id=community_id)
    if not home_page_settings:
      return [], None
    return [t.simple_json() for t in home_page_settings], None


  def create_home_page_setting(self, args) -> (dict, MassEnergizeAPIError):
    try:
      new_home_page_setting = HomePageSettings.create(**args)
      new_home_page_setting.save()
      return new_home_page_setting.full_json(), None
    except Exception:
      return None, ServerError()


  def update_home_page_setting(self, home_page_setting_id, args) -> (dict, MassEnergizeAPIError):
    home_page_setting = HomePageSettings.objects.filter(id=home_page_setting_id)
    if not home_page_setting:
      return None, InvalidResourceError()
    home_page_setting.update(**args)
    return home_page_setting.full_json(), None


  def delete_home_page_setting(self, home_page_setting_id) -> (dict, MassEnergizeAPIError):
    home_page_settings = HomePageSettings.objects.filter(id=home_page_setting_id)
    if not home_page_settings:
      return None, InvalidResourceError()


  def list_home_page_settings_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    home_page_settings = HomePageSettings.objects.filter(community__id = community_id)
    return [t.simple_json() for t in home_page_settings], None


  def list_home_page_settings_for_super_admin(self):
    try:
      home_page_settings = HomePageSettings.objects.all()
      return [t.simple_json() for t in home_page_settings], None
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(str(e))