from django.urls import path
from .views import *

urlpatterns = [
    path('api/audio/upload/', AudioUploadView.as_view(), name='upload-audio'),
    path('api/audio/<int:pk>/', AudioDetailGenericView.as_view(), name='audio-detail-generic'),
    path('api/audio/', MyUploadedAudio.as_view(), name='my_audios')
]
