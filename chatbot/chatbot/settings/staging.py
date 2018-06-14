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

ADMINS = (
  ('Atif', 'mail@atifhaider.com'),
  ('Anubhav', 'anubhav@launchyard.com'),
  ('Mohsin', 'mohsin@launchyard.com'),
  ('Dhilip', 'dhilipsiva@launchyard.com')
)

# EMAIL_BACKEND = 'django_ses.SESBackend'
ALLOWED_HOSTS = ['*']
