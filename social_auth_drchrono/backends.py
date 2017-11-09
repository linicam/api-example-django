from django.contrib.auth.models import User
from social.backends.oauth import BaseOAuth2

from drchrono.helpers import helper
from drchrono.helpers.drchrono_request import get_auth_headers
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
            headers=get_auth_headers(access_token)
        )


def add_user(details, user, uid, *args, **kwargs):
    if user is None:
        user = User.objects.create()
    doctor = Doctor.objects.filter(pk=details['doctor_id'])
    if len(doctor) != 1:
        doctor = Doctor(username=details['username'], doctor_id=details['doctor_id'],
                         uid=uid)
    else:
        doctor = doctor[0]
    doctor.save()
    user.profile.doctor = doctor
    user.profile.access_token = details['access_token']
    user.profile.refresh_token = details['refresh_token']
    user.save()
    # helper.print_object(user)