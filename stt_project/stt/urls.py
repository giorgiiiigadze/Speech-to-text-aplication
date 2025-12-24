from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('api/audio/upload/', AudioUploadView.as_view(), name='upload-audio'),
    path('api/audio/delete/<int:pk>', AudioDeleteView.as_view(), name='delete-audio'),
    path('api/audio/', MyUploadedAudio.as_view(), name='my_audios'),
    path('api/audio/<int:pk>/', AudioDetailGenericView.as_view(), name='audio-detail-generic'),
    path("api/audio/edit-title/<int:pk>/", AudioEditTitleView.as_view(), name="edit-audio-title"),

    path('api/audio/favorite/<int:pk>/', AudioFavoriteToggleView.as_view(), name='audio-favorite-toggle'),

    path('api/audio/comment/<int:audio_id>/', AudioCommentListCreateView.as_view(), name='audio-comments'),
    path('api/audio/comment/delete/<int:pk>/', AudioCommentDeleteView.as_view(), name='audio-comment-delete'),
    path('api/audio/comment/edit_type/<int:pk>/', AudioCommentTypeUpdateView.as_view(), name='audio-comment-type-update'),

    path('api/audio/waveform/<int:pk>/', AudioWaveformView.as_view(), name='audio-waveform'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)