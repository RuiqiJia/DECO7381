from django.contrib import admin
from .models import User, Channel, Message, Topic, Location, Friends, FriendRequest, PrivateChat, PrivateMessage

admin.site.register(User)
admin.site.register(Channel)
admin.site.register(Topic)
admin.site.register(Message)
admin.site.register(Location)
admin.site.register(FriendRequest)
admin.site.register(Friends)
admin.site.register(PrivateChat)
admin.site.register(PrivateMessage)