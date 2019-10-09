from api.api_errors.massenergize_errors import MassEnergizeAPIError
from api.utils.massenergize_response import MassenergizeResponse
from api.store.testimonial import TestimonialStore

class TestimonialService:
  """
  Service Layer for all the testimonials
  """

  def __init__(self):
    self.store =  TestimonialStore()

  def get_testimonial_info(self, testimonial_id) -> (dict, MassEnergizeAPIError):
    testimonial, err = self.store.get_testimonial_info(testimonial_id)
    if err:
      return None, err
    return testimonial

  def list_testimonials(self, testimonial_id) -> (list, MassEnergizeAPIError):
    testimonial, err = self.store.list_testimonials(testimonial_id)
    if err:
      return None, err
    return testimonial, None


  def create_testimonial(self, args) -> (dict, MassEnergizeAPIError):
    testimonial, err = self.store.create_testimonial(args)
    if err:
      return None, err
    return testimonial, None


  def update_testimonial(self, args) -> (dict, MassEnergizeAPIError):
    testimonial, err = self.store.update_testimonial(args)
    if err:
      return None, err
    return testimonial, None

  def delete_testimonial(self, args) -> (dict, MassEnergizeAPIError):
    testimonial, err = self.store.delete_testimonial(args)
    if err:
      return None, err
    return testimonial, None


  def list_testimonials_for_community_admin(self, community_id) -> (list, MassEnergizeAPIError):
    testimonials, err = self.store.list_testimonials_for_community_admin(community_id)
    if err:
      return None, err
    return testimonials, None


  def list_testimonials_for_super_admin(self) -> (list, MassEnergizeAPIError):
    testimonials, err = self.store.list_testimonials_for_super_admin()
    if err:
      return None, err
    return testimonials, None