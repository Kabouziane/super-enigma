import os
from pathlib import Path
from dotenv import load_dotenv
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
DEBUG = os.getenv('DEBUG','True') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS','localhost').split(',')

INSTALLED_APPS = [
    'django.contrib.admin','django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions',
    'django.contrib.messages','django.contrib.staticfiles',
    'assistant','rest_framework','rest_framework_simplejwt','django_ratelimit','django_celery_beat',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware','whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware','django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[BASE_DIR / 'assistant' / 'templates'],'APP_DIRS':True,
             'OPTIONS':{'context_processors':['django.template.context_processors.debug','django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages']}}]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {'default':{'ENGINE':'django.db.backends.sqlite3','NAME':BASE_DIR / 'db.sqlite3'}}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE='en-us'; TIME_ZONE='UTC'; USE_I18N=True; USE_TZ=True
STATIC_URL='/static/'; STATIC_ROOT=BASE_DIR / 'staticfiles'; STATICFILES_DIRS=[BASE_DIR / 'assistant' / 'static']
MEDIA_URL='/media/'; MEDIA_ROOT=BASE_DIR / 'media'; DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'

# Celery
CELERY_BROKER_URL = os.getenv('REDIS_URL','redis://redis:6379/0')
CELERY_RESULT_BACKEND = os.getenv('REDIS_URL','redis://redis:6379/0')

# Email
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND','django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST','')
EMAIL_PORT = int(os.getenv('EMAIL_PORT','0') or 0)
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER','')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD','')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS','False') == 'True'
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL','no-reply@example.com')
INGEST_NOTIFICATION_EMAIL = os.getenv('INGEST_NOTIFICATION_EMAIL','')

# Embeddings
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY','')
EMBEDDINGS_PROVIDER = os.getenv('EMBEDDINGS_PROVIDER','openai')
FAISS_INDEX_PATH = os.getenv('FAISS_INDEX_PATH','./db/faiss.index')
METADATA_PATH = os.getenv('METADATA_PATH','./db/metadata.jsonl')

# Upload limits & rate limit default
MAX_UPLOAD_SIZE = int(os.getenv('MAX_UPLOAD_SIZE','20971520'))  # bytes
RATE_LIMIT = os.getenv('RATE_LIMIT','5/m')

# REST framework (JWT)
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

# Sentry
SENTRY_DSN = os.getenv('SENTRY_DSN','')
if SENTRY_DSN:
    sentry_sdk.init(dsn=SENTRY_DSN, integrations=[DjangoIntegration()], traces_sample_rate=0.1, send_default_pii=True)

# Vector store selection: 'faiss' or 'pinecone'
VECTORSTORE = os.getenv('VECTORSTORE','faiss')

# Logging (structured-ish)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'}
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler','formatter': 'standard'},
    },
    'root': {'handlers': ['console'],'level': 'INFO'},
}
