# -*- coding: utf-8 -*-

"""
Django settings for `yard` project.
"""

import os


# Django settings
# ===============

DEBUG = False
TEMPLATE_DEBUG = False
SECRET_KEY = '3bh%kzi)gd)-c8b49b#vrvkr=%u5a^wf6@gej1904r0ze(nwnm'
ADMINS = (('Dev', 'mjipeo@gmail.com'),)
MANAGERS = ADMINS
ROOT_URLCONF = 'yard.urls'
WSGI_APPLICATION = 'yard.wsgi.application'
LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_L10N = True
USE_TZ = True

BASE_DIR = os.path.realpath(os.path.dirname(__file__))
LOG_DIR = os.path.join(BASE_DIR, 'log')
MEDIA_DIR = os.path.join(BASE_DIR, 'media')
STATIC_DIR = os.path.join(BASE_DIR, 'static')
TEMPLATE_DIRS = (os.path.join(BASE_DIR, 'templates'), )
LOCALE_PATHS = (os.path.join(BASE_DIR, 'locale'), )
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_ROOT = os.path.join(BASE_DIR, 'static/components')
MEDIA_URL = '/media/'
STATIC_URL = '/components/'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'yard.common.context_processors.default',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # Admin
    'django.contrib.admin',
    'django.contrib.admindocs',

    # Project apps
    'yard.apps.account',
    'yard.apps.exchange',
    'yard.apps.trading',
    'yard.apps.study',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

PERIODIC_QUOTE_DATABASE = {
    'host': '14.63.217.41',
    'port': 8088,
    'user': 'root',
    'passwd': 'baadf00d',
    'database': 'yard',
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'verbose': {
            '()': 'yard.utils.log.ColorFormatter',
            'format': '%(asctime)s %(levelname)-8s %(name)-30s %(message)s'
        },
        'simple': {
            '()': 'yard.utils.log.ColorFormatter',
            'format': '%(asctime)s %(levelname)-8s %(message)s'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'yard.log'),
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'yard': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
    }
}

AUTH_USER_MODEL = 'account.User'
LOGIN_URL = '/login'
LOGOUT_URL = '/logout'
LOGIN_REDIRECT_URL = '/'

APPEND_SLASH = False


# Project settings
# ================

# Basic
# -----

VERSION = 1
HOST = 'yard.com'
ALLOWED_HOSTS = ['.{0}'.format(HOST)]


# Email
# -----

CONTACT_EMAIL = 'yard <contact@{host}>'.format(host=HOST)
ALLOWED_DEBUG_EMAIL = ['mjipeo@gmail.com']
EMAIL_DELIMITER = '=====yard====='


# Port
# ----

BRIDGE_SERVER_HOST = 'localhost'
BRIDGE_SERVER_PORT = 9000


# Local settings
# --------------

try:
    from local_settings import *
except ImportError:
    pass
