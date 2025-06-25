from django.urls import path
from . import views

urlpatterns = [
    path('', views.company_info, name='company_info'),  # /upload/
    path('upload/', views.document_upload, name='document_upload'),  # /upload/upload/
    path('success/', views.upload_success, name='upload_success'),
    path('download_report/', views.download_report, name='download_report'),
]
