import pytest
from assistant.tasks import reindex_all_documents_task
from assistant.models import Document
from django.core.files.base import ContentFile

@pytest.mark.django_db
def test_reindex_no_docs(tmp_path, settings):
    # with no documents, task should return ok with empty results
    res = reindex_all_documents_task()
    assert isinstance(res, dict)

@pytest.mark.django_db
def test_reindex_with_doc(tmp_path):
    # create a minimal PDF-like file (header only) - ingestion may skip but task should run
    doc = Document.objects.create(title='test.pdf')
    p = tmp_path / 'test.pdf'
    p.write_bytes(b'%PDF-1.4\n%âãÏÓ\n')
    doc.upload.save('test.pdf', ContentFile(p.read_bytes()))
    res = reindex_all_documents_task()
    assert 'status' in res
