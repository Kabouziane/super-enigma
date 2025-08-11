For celery beat with Django DB scheduler, consider adding django-celery-beat to requirements and migrate the beat tables. The compose file uses django_celery_beat scheduler.

To enable django-celery-beat, add it to requirements (already added) and run: python manage.py migrate django_celery_beat
