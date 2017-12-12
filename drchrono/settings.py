"""
Django settings for drchrono project.

Generated by 'django-admin startproject' using Django 1.8.3.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '=*l&a&rk7jmiw$3euke*z9lu-na!^j^i&ddejfik!ajqlaymmc'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# when restart the server, need to update local db or not, work if create_new is true
SYNC_AT_GV = False
# if set False, won't send requests to drchrono, else send but only create new things, no update local db
# for safe, this should always be True
SYNC_CREATE_NEW = False
SYNC_PERIOD = 1
REDIRECT_TIME = 10

ALLOWED_HOSTS = ['drchrono.hdh9ypmwvt.us-east-1.elasticbeanstalk.com']

# linicam
# SOCIAL_AUTH_DRCHRONO_KEY = 'IkTjfnJytS78j8eiuRB52DXdbIX590LnDU4neuGl'
# tapir
SOCIAL_AUTH_DRCHRONO_KEY = 'ax8am1bvYqQy5p0VvFBQQ4e57UEeJZdum3mdz00X'
# testli1
# SOCIAL_AUTH_DRCHRONO_KEY = '6GbqLQmJHFZLqaJl3bQv6mJSGbXJGiacEL3P8Kx2'

# linicam
# SOCIAL_AUTH_DRCHRONO_SECRET = 'vHCSGGtvzEHAcqI6mewooU5alwzFXypUIp0FBAcju8SAZF6WMHC9kvK' \
#                               'eoSPPbJwT1Y6G9o0RHTsb52PSpBuH1foWWrslHgAQrnw0VW58FxNCWeVm1HAJP8bLn8gAEoQF'
# tapir
SOCIAL_AUTH_DRCHRONO_SECRET = 'LSFBxoyKVPcgz6uOUPhvuNSA8mn7xjH0F134KJPFPgLh5gRmU5IJCHIqA' \
                              'GgbPdozi9kvPfZaojZgWCzzrjQxXdYxskIKkR9i15DmmqFXLYhoqcwKSMlW8njuBteZ09LD'
# testli1
# SOCIAL_AUTH_DRCHRONO_SECRET = 'xqouwHsnmKSqa7ZYMZOLJVJYfGVNWrejgRUDKCr9eLK3HMT3JcFnADz98' \
#                               'omoZo8p9RfdWGMvsm1PZgALY8dsjshKCcXj8vhLQwddbM34M5fbTP98iBprnepa2XHQrn51'


SOCIAL_AUTH_DRCHRONO_AUTH_EXTRA_ARGUMENTS = {
    'access_type': 'offline',
    'approval_prompt': 'auto'
}

LOGIN_URL = '/'
SOCIAL_AUTH_DRCHRONO_LOGIN_REDIRECT_URL = '/identity/'
SOCIAL_AUTH_DRCHRONO_LOGIN_ERROR_URL = '/oauth'
DISCONNECT_REDIRECT_URL = '/'
IDENTITY_URL = '/identity/'  # same to that in urls.py

MEDIA_ROOT = 'E:/pro/api-example-django/drchrono/static/media'
# MEDIA_URL

ADMINS = [('linicam', 'wjlistruggle@gmail.com'), ]

SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    # 'social.pipeline.user.get_username',
    # 'social.pipeline.user.create_user',
    'social_auth_drchrono.backends.add_user',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details',
    'social_auth_drchrono.backends.bind_doctor',
)

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'drchrono',
    'social.apps.django_app.default',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'social.apps.django_app.middleware.SocialAuthExceptionMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'social_auth_drchrono.backends.drchronoOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

ROOT_URLCONF = 'drchrono.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates').replace('\\', '/'), ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social.apps.django_app.context_processors.backends',
                'social.apps.django_app.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'drchrono.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

# USE_TZ = True # timezone support

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'
DISPLAY_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DATE_FORMAT = '%Y-%m-%d'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/drchrono/static/'

# STATIC_ROOT = 'E:/pro/api-example-django/drchrono/static'

STATICFILES_DIRS = []
