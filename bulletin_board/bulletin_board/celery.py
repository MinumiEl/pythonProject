import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bulletin_board.settings')

app = Celery('bulletin_board')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.timezone = 'Europe/Moscow'
app.autodiscover_tasks()
app.conf.beat_schedule = {
    'send_mail_monday_8am': {
        'task': 'board.tasks.send_mail_monday_8am',
        'schedule': crontab(hour=17, minute=12),
    },
}
