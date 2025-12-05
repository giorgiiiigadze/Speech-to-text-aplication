from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('api/audio/upload/', AudioUploadView.as_view(), name='upload-audio'),
    path('api/audio/', MyUploadedAudio.as_view(), name='my_audios'),
    path('api/audio/<int:pk>/', AudioDetailGenericView.as_view(), name='audio-detail-generic'),
    path('api/audio/favorite/<int:pk>/', AudioFavoriteToggleView.as_view(), name='audio-favorite-toggle'),

    path('api/audio/waveform/<int:pk>/', AudioWaveformView.as_view(), name='audio-waveform'),
    path('api/audio/comment/<int:audio_id>/', AudioCommentListCreateView.as_view(), name='audio-comments'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)