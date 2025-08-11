import os
from celery import Celery
from dotenv import load_dotenv
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
app = Celery('config', broker=REDIS_URL, backend=REDIS_URL)
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Example periodic tasks: daily reindex at 02:00 and hourly cleanup
from celery.schedules import crontab
app.conf.beat_schedule = {
    'reindex-all-daily': {
        'task': 'assistant.tasks.reindex_all_documents_task',
        'schedule': crontab(hour=2, minute=0),
        'args': ()
    },
}
