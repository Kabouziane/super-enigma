from django.db import models
class Document(models.Model):
    title = models.CharField(max_length=255)
    upload = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.title} ({self.uploaded_at.date()})"
