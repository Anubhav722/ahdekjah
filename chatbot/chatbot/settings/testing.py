from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': get_env_variable('CHATBOT_DBNAME'),
        'USER': get_env_variable('CHATBOT_DBUSER'),
        'PASSWORD': get_env_variable('CHATBOT_DBPASSWORD'),
        'HOST': get_env_variable('CHATBOT_DBHOST'),
        'PORT': '',
    }
}

ALLOWED_HOSTS = ['*']
