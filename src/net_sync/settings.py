"""
Django settings for net_sync project.

Generated by 'django-admin startproject' using Django 2.2.13.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import json

# current version
__version__ = "0.11.4"

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# try get custom settings
try:
    json_file = os.path.join(BASE_DIR, "net_sync", "mysettings.json")
    with open(json_file, encoding='utf-8') as f:
        USER_SETTINGS = json.load(f)
except:
    USER_SETTINGS = {}

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'k41a#*+rw^aqnorst9hwh@42)m4joe(&$qvw)y6x5&2*orf-3a'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = USER_SETTINGS.get('DEBUG', True)

ALLOWED_HOSTS = USER_SETTINGS.get('ALLOWED_HOSTS', ['*'])

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # third
    'django_extensions',

    # own
    'apps.applications',
]

SHELL_PLUS = 'notebook'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'net_sync.urls'

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

WSGI_APPLICATION = 'net_sync.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = USER_SETTINGS.get('DATABASES') or {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = USER_SETTINGS.get('LANGUAGE_CODE', 'en-us')
TIME_ZONE = USER_SETTINGS.get('TIME_ZONE', 'America/Argentina/Buenos_Aires')
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
    #'/var/www/static/',
]

STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'publish/static')
MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'publish/media')

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/logout/?next=/'


### APP SETTINGS ###

REGISTERED_APPS = (
    ('nettime6', 'NetTime 6'),
    ('manager', 'SPEC Manager DB'),
    ('manager_api', 'SPEC Manager API'),
    ('visma', 'Visma RH'),
    ('exactian', 'Exactian'),
    ('certronic', 'Certronic')
)

REGISTERED_PARAMS = (
    ('host', 'Host'),
    ('server', 'Server'),
    ('instance', 'Instance'),
    ('user', 'User'),
    ('password', 'Password'),
    ('driver', 'Driver'),
    ('port', 'Port'),
    ('database', 'Database'),
    ('controller', 'Controller'),
    ('apikey', 'API-Key'),
)

CONNECTORS = {
    'clockings': {
        'from': {
            'manager_api': {
                'class_': 'specmanagerapi.Client',  # is connector
                'method': 'get_clockings',
            }
        },
        'to': {
            'certronic': {
                'class_': 'certronic.Client',
                'method': 'post_clockings',
            }
        }
    },
    'employees': {
        'from': {
            'nettime6': {
                'class_': 'nettime6.Client',
                'method': 'get_employees',
            },
            'manager': {
                'class_': 'specmanagerdb.Client',
                'method': 'get_employees',
            },
            'visma': {
                'class_': 'visma.Client',
                'method': 'get_employees',
            },
            'exactian': {
                'class_': 'exactian.Client',
                'method': 'get_employees',
            },
            'certronic': {
                'class_': 'certronic.Client',
                'method': 'get_employees',
            },
        },
        'to': {
            'nettime6': {
                'class_': 'nettime6.Client',
                'method': 'post_employees',
            },
            'manager': {
                'class_': 'specmanagerdb.Client',
                'method': 'post_employees',
            },
            'manager_api': {
                'class_': 'specmanagerapi.Client',
                'method': 'post_employees'
            }
        }
    },
    'structure': {
        'from': {
            'manager': {
                'class_': 'specmanagerdb.Client',
                'method': 'get_employees',
            }
        },
        'to': {
            'nettime6': {
                'class_': 'nettime6.Client',
                'method': 'post_departments',
            }
        }
    },
    'results': {
        'from': {
            'nettime6': {
                'class_': 'nettime6.Client',
                'method': 'get_result_syncs',
            },
            'manager': {
                'class_': 'specmanagerdb.Client',
                'method': 'get_results',
            }
        },
        'to': {
            'visma': {
                'class_': 'visma.Client',
                'method': 'post_payments',
            }
        }
    }
}

# format funcs for sync choices
AVAILABLE_FUNCS = [(k, k.capitalize()) for k in CONNECTORS.keys()]

TASK_STATUS = (
    ('0', 'Pending'),   # normal state
    ('1', 'Running'),   # executing
    ('2', 'Queued'),    # manual/forced pending state
)

PARAM_TYPES = (
    ('python', 'Default'),
    ('json', 'JSON'),
)
