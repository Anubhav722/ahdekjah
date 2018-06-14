from .base import *

DEBUG = False

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': get_env_variable('CHATBOT_DBNAME'),
        'USER': get_env_variable('CHATBOT_DBUSER'),
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

ADMINS = (
  ('Atif', 'mail@atifhaider.com'),
  ('Anubhav', 'anubhav@launchyard.com'),
  ('Mohsin', 'mohsin@launchyard.com'),
  ('Dhilip', 'dhilipsiva@launchyard.com')
)

AIRCTO_ADMINS = ['team@aircto.com']

ALLOWED_HOSTS = ['*']

# EMAIL_BACKEND = 'django_ses.SESBackend'
