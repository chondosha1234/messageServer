from django.urls import path
from . import views

urlpatterns = [
    path('messages/send/', views.send_message, name='send_message'),
    path('messages/<int:group_id>', views.get_messages),
    path('groups/create', views.create_group),
    path('users/<int:user_id>/groups/', views.get_group_list),
    path('conversations/create', views.create_conversation),
    path('users/<int:group_id>/conversations', views.get_conversation_list),
    path('users/<int:user_id</add_friend', views.add_friend)
]
