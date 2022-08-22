from django.contrib import admin
from .models import User, Channel, Message, Topic

admin.site.register(User)
admin.site.register(Channel)
admin.site.register(Topic)
admin.site.register(Message)