from django.urls import path
from .views import *

urlpatterns = [
    path('audio/upload/', AudioUploadView.as_view(), name='upload-audio'),
    path('audio/status/<int:pk>/', AudioStatusView.as_view(), name='stt-status'),
    path('audio/<int:pk>/', AudioDetailGenericView.as_view(), name='audio-detail-generic'),
    path('audio/my_audios/', MyUploadedAudio.as_view(), name='my_audios')
]
