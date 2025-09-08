import os
from celery import Celery
from decouple import config


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trendsage.settings')

app = Celery('trendsage')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
