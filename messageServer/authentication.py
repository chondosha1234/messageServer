from messageServer.models import User
from django.contrib.auth.backends import ModelBackend
import logging

logger = logging.getLogger('django')

class CustomAuthenticationBackend(object):

    def authenticate(self, request, username, password):
        logger.info(f'username and password in authenticate: {username} and {password}')
        try:
            user = User.objects.get(username=username)
            logger.info(f'user in authenticate: {user}')
            logger.info(f'result of check password in authenticate: {user.check_password(password)}')
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
