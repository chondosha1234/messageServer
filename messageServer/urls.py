from django.urls import path
from . import views

urlpatterns = [
    path('messages/send/', views.send_message),
    path('messages/<int:group_id>', views.get_messages),
    path('users/<int:user_id>/groups/', views.get_group_list)
]
