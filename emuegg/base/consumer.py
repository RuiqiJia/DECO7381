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
        command = text_data.get("command", None)
        if command == "join":
            print("joining room: " + str(text_data['room']))
            await self.join_room(text_data["room"])
        elif command == "leave":
            await self.leave_room(text_data["room"])
        elif command == "send":
            await self.send_room(text_data["room"], text_data["message"])
        elif command == "get_room_chat_messages":
            
            # room = await get_room_or_error(content['room_id'], self.scope["user"])
            # payload = await get_room_chat_messages(room, content['page_number'])
            if payload != None:
                payload = json.loads(payload)
                await self.send_messages_payload(payload['messages'], payload['new_page_number'])
            await self.display_progress_bar(False)

    def chat_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps({
            'message': message
        }))
        
         