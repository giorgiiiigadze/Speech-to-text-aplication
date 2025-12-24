from rest_framework.throttling import UserRateThrottle
from rest_framework.throttling import SimpleRateThrottle

class BurstRateThrottle(UserRateThrottle):
    scope = 'burst'

class SustainedRateThrottle(UserRateThrottle):
    scope = 'sustained'

class AudioEditTitleThrottle(SimpleRateThrottle):
    scope = 'edit_audio_title'

    def get_cache_key(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return None
        return f"edit_audio_title_{request.user.id}"
    
class AudioCommentThrottle(SimpleRateThrottle):
    scope = "audio_comments"

    def get_cache_key(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return None
        return f"audio_comments_{request.user.id}"
    
class AudioCommentDeleteThrottle(SimpleRateThrottle):
    scope = "audio_comment_delete"

    def get_cache_key(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return None
        return f"audio_comment_delete_{request.user.id}"
