import os, io, json
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from ratelimit.decorators import ratelimit
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Document
from .tasks import ingest_document_task
from celery.result import AsyncResult
from .ingest import is_pdf_bytes

def index(request):
    docs = Document.objects.all().order_by('-uploaded_at')[:20]
    return render(request, 'assistant/index.html', {'documents': docs})

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@ratelimit(key='ip', rate=settings.RATE_LIMIT, block=True)
def upload(request):
    f = request.FILES.get('file')
    if not f: return HttpResponseBadRequest('No file uploaded')
    if not f.name.lower().endswith('.pdf'): return HttpResponseBadRequest('Only PDF files supported')
    if f.size > settings.MAX_UPLOAD_SIZE: return HttpResponseBadRequest('File too large')
    data = f.read()
    if not is_pdf_bytes(data[:4]):
        return HttpResponseBadRequest('Uploaded file is not a valid PDF (header mismatch)')
    doc = Document.objects.create(title=f.name, upload=f)
    task = ingest_document_task.delay(data, f.name)
    return JsonResponse({'success': True, 'task_id': task.id})

@api_view(['GET'])
@permission_classes([AllowAny])
def task_status(request):
    task_id = request.GET.get('task_id')
    if not task_id: return HttpResponseBadRequest('task_id required')
    res = AsyncResult(task_id)
    info = {'status': res.status}
    if res.ready():
        try:
            info['result'] = res.result
        except Exception as e:
            info['result'] = str(e)
    return JsonResponse(info)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@ratelimit(key='ip', rate=settings.RATE_LIMIT, block=True)
def query_view(request):
    try:
        payload = json.loads(request.body.decode('utf-8'))
        q = payload.get('query','').strip()
        top_k = int(payload.get('top_k',5))
    except Exception:
        return HttpResponseBadRequest('Invalid payload')
    if not q: return HttpResponseBadRequest('Empty query')
    from .ai import answer_query
    out = answer_query(q, top_k=top_k)
    return JsonResponse(out)
