from contextlib import nullcontext
from re import I
from channels.generic.websocket import AsyncJsonWebsocketConsumer
import json
from asgiref.sync import async_to_sync
from .models import User

class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']
        # self.room_group_name = f'chat_{user.id}'

        # self.channel_layer.group_add(
        #     self.room_group_name,
        #     self.channel_name
        # )
        
        # self.channel_layer.group_add(
        #     self.room_group_name,
        #     self.channel_name
        # )
        await self.accept()
        self.room_id = None
        
        

    async def disconnect(self, close_code):
        return nullcontext

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender_id = text_data_json.get('sender')
        receiver_id = text_data_json.get('receiver')
        sender = User.objects.get(id=sender_id)
        receiver = User.objects.get(id=receiver_id)

        receiver_room_group_name = f'chat_{receiver_id}'
        self_user = self.scope['user']
        res = {
            'message': message,
            'sender': self_user.id,

        }

        async_to_sync(self.channel_layer.group_send)(
            receiver_room_group_name,
            {
                'type': 'chat_message',
                'message': json.dumps(res),
            }
        )
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': json.dumps(res),
            }
        )
        

    def chat_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps({
            'message': message
        }))
        
         