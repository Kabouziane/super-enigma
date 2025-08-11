from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload, name='upload'),
    path('task-status/', views.task_status, name='task_status'),
    path('query/', views.query_view, name='query'),
]
