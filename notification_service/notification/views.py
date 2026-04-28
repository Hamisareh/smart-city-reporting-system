# notification_service/notification/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from .models import Notification
from .serializers import NotificationSerializer
import logging

logger = logging.getLogger(__name__)

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        user_id = getattr(self.request, 'user_id', None)
        print(f"🔍 [NOTIF] get_queryset - user_id from middleware: {user_id}")
        logger.info(f"📋 get_queryset: user_id={user_id}")
        
        if user_id:
            qs = Notification.objects.filter(user_id=user_id).order_by('-created_at')
            print(f"🔍 [NOTIF] Found {qs.count()} notifications for user {user_id}")
            return qs
        print(f"🔍 [NOTIF] No user_id, returning empty queryset")
        return Notification.objects.none()
    
    def list(self, request, *args, **kwargs):
        print(f"🔍 [NOTIF] list() called - request.user_id={getattr(request, 'user_id', None)}")
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        print(f"🔍 [NOTIF] Returning {len(serializer.data)} notifications")
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.read = True
        notification.save()
        return Response({'status': 'marked as read'})