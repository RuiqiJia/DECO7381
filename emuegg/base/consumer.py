from channels.generic.websocket import AsyncJsonWebsocketConsumer
import json
from asgiref.sync import async_to_sync
from .models import Friends, PrivateChat, User
from django.core.serializers import serialize
from django.core.serializers.python import Serializer
from channels.db import database_sync_to_async
from .models import PrivateMessage

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


    # async def disconnect(self, close_code):
    #     return nullcontext
    
    async def join(self, room_id):
        room = await get_room(room_id, self.scope['user'])
        await self.channel_layer.group_add(
			room.group_name,
			self.channel_name,
		)
        await self.send_json({
            "join": str(room.id)
        })

    async def receive(self, text_data):
        command = text_data.get("command", None)
        if command == "join":
            print("joining room: " + str(text_data['room']))
            await self.join(text_data["room"])
        elif command == "leave":
            await self.leave_room(text_data["room"])
        elif command == "send":
            await self.send_room(text_data["room"], text_data["message"])
        elif command == "get_room_chat_messages":
            pass
        elif command == "user_info":
            room = await get_room(text_data["room_id"], self.scope["user"])
            data = user_info(room, self.scope["user"])
            if data != None:
                await self.send_json({"user_info": data["user_info"]})

@database_sync_to_async
def chat_message(user, room, message):
    return PrivateMessage.objects.create(user=user, chat_room=room, message=message)
    
        
@database_sync_to_async        
def get_room(room_id, user):
    room = PrivateChat.objects.get(id=room_id)
    friends = Friends.objects.filter(user=user).friend.all()
    if user != room.user1 and user != room.user2:
        raise Exception("User is not allowed to access this room")
    if not room.user2 in friends:
        raise Exception("User is not friends with the other user")
    return room

def user_info(room, user):
    other = room.user1
    if other == user:
        other = room.user2
    data = {}
    serializer = UserSerializer()
    data['user_info'] = serializer.serialize([other])[0]
    print(serializer.serialize([other])[0])
    return json.dumps(data)

class UserSerializer(Serializer):
    def get_dump_object(self, obj):
        return {
            'id': obj.id,
            'username': obj.username,
            'email': obj.email,
        }
    
    def end_object(self, obj):
        self.objects.append(self.get_dump_object(obj))
        return super().end_object(obj)
    
    def getvalue(self):
        return json.dumps(self.objects)


        