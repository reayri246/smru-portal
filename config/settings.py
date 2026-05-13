"""
Django settings for config project - Production Ready.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
import os
from decouple import config, Csv

# Monkey patch mimetypes to avoid hanging on Windows registry read
import mimetypes
if os.name == 'nt':
    mimetypes.MimeTypes.read_windows_registry = lambda self: None

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
DEBUG = config('DEBUG', default=False, cast=bool)
SECRET_KEY = config('SECRET_KEY')
ALLOWED_HOSTS = config('ALLOWED_HOSTS',default='127.0.0.1,localhost', cast=Csv())

# Database environment variables (for cloud deployment)
# Add these to your .env file or environment variables:
# DATABASE_ENGINE=django.db.backends.postgresql
# DATABASE_NAME=your_database_name
# DATABASE_USER=your_database_user
# DATABASE_PASSWORD=your_database_password
# DATABASE_HOST=your_database_host
# DATABASE_PORT=5432
# DATABASE_URL=postgresql://user:password@host:port/database (for Heroku-style URLs)


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'smru',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'smru' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.csrf',
            ],
        },
    },
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

# Dynamic database configuration using environment variables
DATABASES = {
    'default': {
        'ENGINE': config('DATABASE_ENGINE', default='django.db.backends.sqlite3'),
        'NAME': config('DATABASE_NAME', default=str(BASE_DIR / 'db.sqlite3')),
        'USER': config('DATABASE_USER', default=''),
        'PASSWORD': config('DATABASE_PASSWORD', default=''),
        'HOST': config('DATABASE_HOST', default=''),
        'PORT': config('DATABASE_PORT', default=''),
    }
}

# For PostgreSQL (recommended for production)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'your_database_name',          # Database name
#         'USER': 'your_database_user',          # Database username
#         'PASSWORD': 'your_database_password',  # Database password
#         'HOST': 'your_database_host',          # Database host (e.g., 'localhost', 'db.yourproject.cloud')
#         'PORT': '5432',                        # Database port (default: 5432 for PostgreSQL)
#         'OPTIONS': {
#             'sslmode': 'require',              # For cloud databases with SSL
#         },
#     }
# }

# For MySQL/MariaDB
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'your_database_name',          # Database name
#         'USER': 'your_database_user',          # Database username
#         'PASSWORD': 'your_database_password',  # Database password
#         'HOST': 'your_database_host',          # Database host
#         'PORT': '3306',                        # Database port (default: 3306 for MySQL)
#         'OPTIONS': {
#             'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
#         },
#     }
# }

# For AWS RDS PostgreSQL
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'your_rds_db_name',
#         'USER': 'your_rds_username',
#         'PASSWORD': 'your_rds_password',
#         'HOST': 'your-rds-instance.region.rds.amazonaws.com',
#         'PORT': '5432',
#     }
# }

# For Google Cloud SQL PostgreSQL
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'your_cloudsql_db_name',
#         'USER': 'your_cloudsql_username',
#         'PASSWORD': 'your_cloudsql_password',
#         'HOST': '/cloudsql/your-project:region:instance-name',  # For App Engine
#         # OR
#         # 'HOST': '127.0.0.1',  # For Cloud Run with proxy
#         'PORT': '5432',
#     }
# }

# For Heroku PostgreSQL (using DATABASE_URL environment variable)
# import dj_database_url
# DATABASES = {
#     'default': dj_database_url.config(
#         default=config('DATABASE_URL', default='sqlite:///db.sqlite3')
#     )
# }

# For DigitalOcean Managed Database
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'your_do_db_name',
#         'USER': 'your_do_username',
#         'PASSWORD': 'your_do_password',
#         'HOST': 'your-do-db-host.db.ondigitalocean.com',
#         'PORT': '25060',  # Default DO managed DB port
#         'OPTIONS': {
#             'sslmode': 'require',
#         },
#     }
# }

# Dynamic database configuration using environment variables
# Uncomment the code below to use environment variables for database configuration
# DATABASES = {
#     'default': {
#         'ENGINE': config('DATABASE_ENGINE', default='django.db.backends.sqlite3'),
#         'NAME': config('DATABASE_NAME', default=str(BASE_DIR / 'db.sqlite3')),
#         'USER': config('DATABASE_USER', default=''),
#         'PASSWORD': config('DATABASE_PASSWORD', default=''),
#         'HOST': config('DATABASE_HOST', default=''),
#         'PORT': config('DATABASE_PORT', default=''),
#     }
# }

# Alternative: Using DATABASE_URL for Heroku, Render, etc.
# import dj_database_url
# DATABASES = {
#     'default': dj_database_url.config(
#         default=config('DATABASE_URL', default=f'sqlite:///{BASE_DIR / "db.sqlite3"}')
#     )
# }


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


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
# Use ManifestStaticFilesStorage only in production
if not DEBUG:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ======================== SECURITY SETTINGS ========================

# Security Headers
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=0, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = config('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=False, cast=bool)
SECURE_HSTS_PRELOAD = config('SECURE_HSTS_PRELOAD', default=False, cast=bool)
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=False, cast=bool)
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=False, cast=bool)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=False, cast=bool)

# CSRF Configuration - includes production domain by default
csrf_origins = config('CSRF_TRUSTED_ORIGINS', default='https://smru-portal-4.onrender.com,http://localhost:8000,http://127.0.0.1:8000', cast=Csv())
CSRF_TRUSTED_ORIGINS = csrf_origins if csrf_origins else ['https://smru-portal-4.onrender.com', 'http://localhost:8000', 'http://127.0.0.1:8000']

# Additional Security
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    'default-src': ("'self'",),
    'script-src': ("'self'", "'unsafe-inline'", 'cdn.jsdelivr.net'),
    'style-src': ("'self'", "'unsafe-inline'", 'cdn.jsdelivr.net'),
    'img-src': ("'self'", 'data:', 'https:'),
}

# ======================== LOGGING CONFIGURATION ========================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024 * 1024 * 15,
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
        'smru': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Create logs directory if it doesn't exist
import os
LOGS_DIR = BASE_DIR / 'logs'
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR, exist_ok=True)

# ======================== EMAIL CONFIGURATION ========================

EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER)

# Optional Twilio WhatsApp integration for complaint notifications
TWILIO_ACCOUNT_SID = config('TWILIO_ACCOUNT_SID', default='')
TWILIO_AUTH_TOKEN = config('TWILIO_AUTH_TOKEN', default='')
TWILIO_WHATSAPP_FROM = config('TWILIO_WHATSAPP_FROM', default='')

# ======================== PAGINATION ========================

PAGINATION_ITEMS_PER_PAGE = 20

# ======================== CACHING ========================

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# ======================== SESSION CONFIGURATION ========================

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Auto logout when browser is closed
SESSION_SAVE_EVERY_REQUEST = True  # Keep sessions alive while the admin is actively used

# ======================== FILE UPLOAD ========================

FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
MAX_UPLOAD_SIZE = 5242880

# ======================== AUTHENTICATION ========================

LOGIN_URL = 'smru:login'
LOGIN_REDIRECT_URL = 'smru:home'
LOGOUT_REDIRECT_URL = 'smru:home'

# ======================== TIMEZONE ========================

USE_TZ = True
TIME_ZONE = 'Asia/Kolkata'  # IST
