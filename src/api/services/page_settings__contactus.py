from api.api_errors.massenergize_errors import MassEnergizeAPIError
from api.utils.massenergize_response import MassenergizeResponse
from api.store.page_settings__contactus import ContactUsPageSettingsStore

class ContactUsPageSettingsService:
  """
  Service Layer for all the contact_us_page_settings
  """

  def __init__(self):
    self.store =  ContactUsPageSettingsStore()

  def get_contact_us_page_setting_info(self, contact_us_page_setting_id) -> (dict, MassEnergizeAPIError):
    contact_us_page_setting, err = self.store.get_contact_us_page_setting_info(contact_us_page_setting_id)
    if err:
      return None, err
    return contact_us_page_setting

  def list_contact_us_page_settings(self, contact_us_page_setting_id) -> (list, MassEnergizeAPIError):
    contact_us_page_setting, err = self.store.list_contact_us_page_settings(contact_us_page_setting_id)
    if err:
      return None, err
    return contact_us_page_setting, None


  def create_contact_us_page_setting(self, args) -> (dict, MassEnergizeAPIError):
    contact_us_page_setting, err = self.store.create_contact_us_page_setting(args)
    if err:
      return None, err
    return contact_us_page_setting, None


  def update_contact_us_page_setting(self, args) -> (dict, MassEnergizeAPIError):
    contact_us_page_setting, err = self.store.update_contact_us_page_setting(args)
    if err:
      return None, err
    return contact_us_page_setting, None

  def delete_contact_us_page_setting(self, args) -> (dict, MassEnergizeAPIError):
    contact_us_page_setting, err = self.store.delete_contact_us_page_setting(args)
    if err:
      return None, err
    return contact_us_page_setting, None


  def list_contact_us_page_settings_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    contact_us_page_settings, err = self.store.list_contact_us_page_settings_for_community_admin(community_id)
    if err:
      return None, err
    return contact_us_page_settings, None


  def list_contact_us_page_settings_for_super_admin(self) -> (list, MassEnergizeAPIError):
    contact_us_page_settings, err = self.store.list_contact_us_page_settings_for_super_admin()
    if err:
      return None, err
    return contact_us_page_settings, None