from django.urls import path
from . import views

urlpatterns = [
    path('messages/send/', views.send_message, name='send_message'),
    path('messages/<int:conversation_id>', views.get_messages, name='get_messages'),
    path('groups/create', views.create_group, name='create_group'),
    path('users/<int:user_id>/groups/', views.get_group_list, name='get_group_list'),
    path('conversations/create', views.create_conversation, name='create_conversation'),
    path('users/<int:group_id>/conversations', views.get_conversation_list, name='get_conversation_list'),
    path('users/<int:user_id</add_friend', views.add_friend, name='add_friend')
]
