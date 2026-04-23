from pathlib import Path

# -----------------------------
# BASE DIRECTORY
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------
# SECURITY
# -----------------------------
SECRET_KEY = 'django-insecure-6_-2d+p=%3pu9_fe0a06a&-nx-ed2h1_r$35j2v=okxwgx6$i#'

DEBUG = True

ALLOWED_HOSTS = []

# -----------------------------
# APPLICATIONS
# -----------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Your apps
    'accounts',

    # Third-party
    'rest_framework',
]

# -----------------------------
# MIDDLEWARE
# -----------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# -----------------------------
# URLS & TEMPLATES
# -----------------------------
ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        # 🔥 THIS IS THE FIX
        'DIRS': [BASE_DIR / 'templates'],

        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# -----------------------------
# DATABASE (SQL SERVER)
# -----------------------------
DATABASES = {
    "default": {
        "ENGINE": "mssql",
        "NAME": "DataCapture",
        "USER": "datacapture_user",
        "PASSWORD": "Passkey@123",
        "HOST": "192.168.10.28",
        "PORT": "1433",
        "OPTIONS": {
            "driver": "ODBC Driver 17 for SQL Server",
        },
    }
}

# -----------------------------
# CUSTOM USER MODEL (CRITICAL)
# -----------------------------
AUTH_USER_MODEL = 'accounts.User'

# -----------------------------
# PASSWORD VALIDATION
# -----------------------------
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

# -----------------------------
# INTERNATIONALIZATION
# -----------------------------
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Harare'

USE_I18N = True

USE_TZ = True

# -----------------------------
# STATIC FILES
# -----------------------------
STATIC_URL = 'static/'

# -----------------------------
# DEFAULT PRIMARY KEY
# -----------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'