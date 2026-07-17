"""WebSocket consumer for real-time notifications"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope['user'].is_anonymous:
            await self.close()
            return

        self.user = self.scope['user']
        self.group_name = f'notifications_{self.user.id}'

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # Send unread count on connect
        count = await self.get_unread_count()
        await self.send(json.dumps({
            'type': 'unread_count',
            'count': count,
        }))

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get('type') == 'mark_read':
            await self.mark_notification_read(data.get('id'))

    async def notification_message(self, event):
        """Handle notification messages sent to the group"""
        await self.send(json.dumps({
            'type': 'notification',
            'id': event['id'],
            'title': event['title'],
            'message': event['message'],
            'notification_type': event['notification_type'],
            'priority': event['priority'],
            'action_url': event.get('action_url', ''),
            'created_at': event['created_at'],
        }))

    @database_sync_to_async
    def get_unread_count(self):
        from notifications.models import Notification
        return Notification.objects.filter(recipient=self.user, is_read=False).count()

    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        from notifications.models import Notification
        try:
            notif = Notification.objects.get(id=notification_id, recipient=self.user)
            notif.mark_as_read()
        except Notification.DoesNotExist:
            pass
