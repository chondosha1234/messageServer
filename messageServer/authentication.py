from messageServer.models import User
from django.contrib.auth.backends import ModelBackend

class CustomAuthenticationBackend(object):

    def authenticate(self, request, name, password):
        try:
            user = User.objects.get(name=name)
            if user.check_password(password):
                return user
            else:
                return None
        except User.DoesNotExist:
            return None

    def get_user(self, name):
        try:
            return User.objects.get(name=name)
        except User.DoesNotExist:
            return None
