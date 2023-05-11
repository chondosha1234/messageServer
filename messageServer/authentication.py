from messageServer.models import User
from django.contrib.auth.backends import ModelBackend

class CustomAuthenticationBackend(object):

    def authenticate(self, request, username, password):
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                return user
            else:
                return None
        except User.DoesNotExist:
            return None

    def get_user(self, username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None
