from rest_framework.throttling import UserRateThrottle

class ChatThrottle(UserRateThrottle):
    scope = "chat"
