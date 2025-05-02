from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')
app.config_from_object(settings, namespace='CELERY')

# Celery bet settings
app.conf.beat_schedule = {
    
    'notifications_task': {
        'task': 'modules.tasks.notifications_task',  
        'schedule': crontab(minute='*/2'), 
    }
}

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')