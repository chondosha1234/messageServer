from django.urls import path
from . import views
from messageServer.views import CreateUserView, LoginView, LogoutView


urlpatterns = [
    path('messages/send/', views.send_message, name='send_message'),
    path('messages/<uuid:conversation_id>', views.get_messages, name='get_messages'),
    path('groups/create', views.create_group, name='create_group'),
    path('groups/<uuid:group_id>/get_group', views.get_group, name='get_group'),
    path('groups/<uuid:group_id>/get_member_list', views.get_member_list, name='get_member_list'),
    path('groups/<uuid:group_id>/set_picture', views.set_group_picture, name='set_group_picture'),
    path('groups/<uuid:group_id>/<uuid:user_id>/add_member', views.add_member, name='add_member'),
    path('groups/<uuid:group_id>/<uuid:user_id>/remove_member', views.remove_member, name='remove_member'),
    path('groups/create_conversation', views.create_conversation, name='create_conversation'),
    path('groups/<uuid:group_id>/conversations', views.get_conversation_list, name='get_conversation_list'),
    path('groups/conversation/<uuid:conversation_id>', views.get_conversation, name='get_conversation'),
    path('groups/conversation/<uuid:conversation_id>/set_picture', views.set_conversation_picture, name='set_conversation_picture'),
    path('users/groups', views.get_group_list, name='get_group_list'),
    path('users/<uuid:user_id>/add_friend', views.add_friend, name='add_friend'),
    path('users/<uuid:user_id>/remove_friend', views.remove_friend, name='remove_friend'),
    path('users/get_friends_list', views.get_friends_list, name='get_friends_list'),
    path('users/create_user', CreateUserView.as_view(), name='create_user'),
    path('users/get_current_user', views.get_current_user, name='get_current_user'),
    path('users/set_picture', views.set_profile_picture, name='set_profile_picture'),
    path('users/set_fcm_token', views.set_fcm_token, name='set_fcm_token'),
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout')
]
