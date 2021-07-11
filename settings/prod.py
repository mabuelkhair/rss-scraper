from datetime import timedelta
import environ

from .default import *  # noqa

env = environ.Env()
environ.Env.read_env()

DEBUG = False
SECRET_KEY = env.str('SECRET_KEY')
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST_USER = env.str('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD')

CELERY_MAX_RETRIES = env.int('CELERY_MAX_RETRIES', default=3)
CELERY_RETRY_DELAY = env.int('CELERY_RETRY_DELAY', default=60)

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=env.int('ACCESS_TOKEN_LIFETIME', default=15)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=env.int('REFRESH_TOKEN_LIFETIME', default=14)),
}

REST_FRAMEWORK['PAGE_SIZE'] = env.int('API_PAGE_SIZE', default=15)  # noqa
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env.str('DB_NAME'),
        'USER': env.str('DB_USERNAME'),
        'PASSWORD': env.str('DB_PASSWORD'),
        'HOST': env.str('DB_HOST'),
        'PORT': env.str('DB_PORT', default='5432'),
    }
}
