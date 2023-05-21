from messageServer.models import User
from django.contrib.auth.backends import ModelBackend
from rest_framework.authtoken.models import Token
import logging

logger = logging.getLogger('django')

class CustomAuthenticationBackend(object):

    def authenticate(self, request, username, password):
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                token, _ = Token.objects.get_or_create(user=user)
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
