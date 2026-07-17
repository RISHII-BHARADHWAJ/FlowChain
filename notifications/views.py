"""Notifications ViewSet and views"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        from notifications.models import Notification
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')

    def get_serializer_class(self):
        from notifications.serializers import NotificationSerializer
        return NotificationSerializer

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notif = self.get_object()
        notif.mark_as_read()
        return Response({'status': 'read'})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        from notifications.models import Notification
        Notification.objects.filter(recipient=request.user, is_read=False).update(
            is_read=True, read_at=timezone.now()
        )
        return Response({'status': 'all read'})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        from notifications.models import Notification
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return Response({'count': count})
