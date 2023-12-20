# settings/production.py
from .base import *
from decouple import config, Csv
import dj_database_url

# Security
DEBUG = config('DEBUG', default=False, cast=bool)
SECRET_KEY = config('SECRET_KEY')

# Allowed hosts
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

# CORS
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', cast=Csv())

# Database
DATABASES = {
    'default': dj_database_url.config(default=config('DATABASE_URL'))
}
