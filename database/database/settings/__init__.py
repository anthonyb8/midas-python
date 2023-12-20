# settings/__init__.py
from decouple import config
from .base import *

if config('DJANGO_ENV') == 'production':
    from .production import *
else:
    from .development import *
