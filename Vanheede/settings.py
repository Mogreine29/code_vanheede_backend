"""
Django settings for Vanheede project.

Generated by 'django-admin startproject' using Django 3.2.9.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
from global_var import ON_SERVER

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-^p$htcuzj6dr$fve-7n3+0yk)p&heq)78z=(p7_j4^sqdqur)r'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

if ON_SERVER :
  ALLOWED_HOSTS = ['vanheede.ig.umons.ac.be','localhost','db']
else :
  ALLOWED_HOSTS = ['db','localhost']



# Application definition

INSTALLED_APPS = [
    'bulles.apps.BullesConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "corsheaders",
    'rest_framework',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    )
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Vanheede.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Vanheede.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

if ON_SERVER :
  user = 'vanheede'
  password = 'xXZq25d74zsn2-a'
  host = 'db:3306'
else :
  user = 'vanheede'
  password = 'xXZq25d74zsn2-a'
  host = 'db'



DATABASES = {
     'default': {
         'ENGINE': 'django.db.backends.mysql',
         'NAME': 'vanheede',
         'USER': 'vanheede',
         'PASSWORD': 'xXZq25d74zsn2-a',
         'HOST': 'db',
         'PORT': '3306',
     }
    #'default': {
    #    'ENGINE': 'django.db.backends.mysql',
    #    'NAME': 'vanheede',
    #    'USER': 'root',
    #    'PASSWORD': '',
    #    'HOST': 'localhost',
    #    'PORT': '3306',
    #}
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

CORS_ALLOW_ALL_ORIGINS = True # If this is used then `CORS_ALLOWED_ORIGINS` will not have any effect
CORS_ALLOW_CREDENTIALS = True
# CORS_ALLOWED_ORIGINS = [
#    #"http://" 
#    "http://127.0.0.1:5501",
#  ] # If this is used, then not need to use `CORS_ALLOW_ALL_ORIGINS = True`
# CORS_ALLOWED_ORIGIN_REGEXES = [
#     #"http://127.0.0.1:5500" , 
#    # "",
# ]

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-US'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True



LOGIN_URL = 'index'
LOGIN_REDIRECT_URL = 'accueil'
LOGOUT_REDIRECT_URL = 'index'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'