from social.backends.oauth import BaseOAuth2

from drchrono.helpers import helper
from drchrono.helpers.helper import DrchronoRequest
from drchrono.models import Doctor


class drchronoOAuth2(BaseOAuth2):
    """
    drchrono OAuth authentication backend
    """

    name = 'drchrono'
    AUTHORIZATION_URL = 'https://drchrono.com/o/authorize/'
    ACCESS_TOKEN_URL = 'https://drchrono.com/o/token/'
    ACCESS_TOKEN_METHOD = 'POST'
    REDIRECT_STATE = False
    USER_DATA_URL = 'https://drchrono.com/api/users/current'
    EXTRA_DATA = [
        ('refresh_token', 'refresh_token'),
        ('expires_in', 'expires_in')
    ]
    # TODO: setup proper token refreshing

    def get_user_details(self, response):
        """
        Return user details from drchrono account
        """
        # for key in response:
        #     print key,'-------',response[key]
        return {
            'username': response.get('username'),
            'doctor_id': response['doctor'],
            'access_token': response['access_token'],
            'refresh_token': response['refresh_token'],
            'practice_group': response['practice_group'],
        }

    def user_data(self, access_token, *args, **kwargs):
        """
        Load user data from the service
        """
        return self.get_json(
            self.USER_DATA_URL,
            headers=helper.get_auth_headers(access_token)
        )


def add_user(details, user, uid, *args, **kwargs):
    try:
        profile = Doctor.objects.get(user=user)
    except Doctor.objects.model.DoesNotExist:
        profile = Doctor(username=details['username'], doctor_id=details['doctor_id'],
                         uid=uid, user=user, access_token=details['access_token'],
                         refresh_token=details['refresh_token'], practice_group=details['practice_group'])
    profile.save()

