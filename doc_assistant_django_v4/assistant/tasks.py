from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .ai import ingest_and_index
from .models import Document
import traceback

@shared_task(bind=True)
def ingest_document_task(self, file_bytes, filename):
    try:
        count = ingest_and_index(file_bytes, filename)
        notify_to = settings.INGEST_NOTIFICATION_EMAIL
        if notify_to:
            subject = f'Document ingestion completed: {filename}'
            message = f'Ingestion finished for {filename}. Indexed {count} chunks.'
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [notify_to], fail_silently=True)
        return {'status':'ok','ingested_chunks': count}
    except Exception as e:
        traceback.print_exc()
        return {'status':'error','error': str(e)}

@shared_task(bind=True)
def reindex_all_documents_task(self):
    try:
        docs = Document.objects.all()
        results = []
        for d in docs:
            with open(d.upload.path, 'rb') as fh:
                res = ingest_and_index(fh.read(), d.title)
                results.append({'doc': d.title, 'chunks': res})
        return {'status':'ok', 'results': results}
    except Exception as e:
        traceback.print_exc()
        return {'status':'error','error': str(e)}
