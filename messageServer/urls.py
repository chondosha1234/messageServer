from django.urls import path
from . import views
from messageServer.views import CreateUserView, LoginView, LogoutView

urlpatterns = [
    path('messages/send/', views.send_message, name='send_message'),
    path('messages/<int:conversation_id>', views.get_messages, name='get_messages'),
    path('groups/create', views.create_group, name='create_group'),
    path('groups/<int:group_id>/get_member_list', views.get_member_list, name='get_member_list'),
    path('groups/<int:group_id>/<int:user_id>/add_member', views.add_member, name='add_member'),
    path('groups/<int:group_id>/<int:user_id>/remove_member', views.remove_member, name='remove_member'),
    path('groups/<int:group_id>/create_conversation', views.create_conversation, name='create_conversation'),
    path('groups/<int:group_id>/conversations', views.get_conversation_list, name='get_conversation_list'),
    path('users/groups', views.get_group_list, name='get_group_list'),
    path('users/<int:user_id>/add_friend', views.add_friend, name='add_friend'),
    path('users/<int:user_id>/remove_friend', views.remove_friend, name='remove_friend'),
    path('users/get_friends_list', views.get_friends_list, name='get_friends_list'),
    path('users/create_user', CreateUserView.as_view(), name='create_user'),
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout')
]
