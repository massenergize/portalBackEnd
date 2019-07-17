from django.urls import path, re_path
from django.conf.urls import url
from .views import *

urlpatterns = [
  url(r'^$', home),
  path('get/page',get_page),
  path('get/todo_actions', get_user_todo_actions),
  path('get/completed_actions', get_user_completed_actions),
  path('get/events', get_all_community_events),
  path('get/events/all', get_all_community_events),
  path('get/event', get_one_event),
  path('get/community_actions', get_community_actions),
  path('get/community_actions/all', get_community_actions),
  path('get/action', get_one_action),
  path('get/profile', get_my_profile),
  path('get/households', get_user_households),
  path('get/household', get_one_household),
  path('get/teams/all', get_community_teams),
  path('get/team', get_one_team),
  path('get/communities', get_all_communities),
  path('get/community', get_one_community),
  path('get/graph', get_one_community_graph),
  path('get/graphs', get_community_graphs),
  path('get/graphs/all', get_community_graphs),
  path('create/account', create_new_user),
  path('create/user', create_new_user),
  path('create/goal', create_goal),
  path('create/household', create_household),
  path('create/real_estate_unit', create_household),
  path('create/team', create_team),
  path('create/event', create_event),
  path('create/location', create_location),
  path('create/community', create_community),
  path('add/team_members', add_team_members),
  path('add/user_action', create_user_action),
  path('subscribe', create_subscriber),
  path('add/subscriber', create_subscriber),
  path('create/subscriber', create_subscriber),
  path('add/testimonial', add_testimonial),
  path('register_for_event', register_user_for_event),
  path('update/user_action', update_user_action),
  path('update/profile', update_profile),
  path('delete/user_action', delete_user_action),
  path('delete/user', delete_user_account),
  path('actions', actions),
  path('test', ping),
  path('ping', ping),
  path('menu/sidebar', get_super_admin_sidebar_menu),
  path('menu/navbar',get_super_admin_navbar_menu),
  path('events', events, name='super_admin_events'),
  path('communities', communities),
]