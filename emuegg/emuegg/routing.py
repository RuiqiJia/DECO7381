from email.mime import application
import webbrowser
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator, OriginValidator

from django.urls import re_path
from ..base import consumer
from ..base.consumer import ChatConsumer
from django.urls import path

# websocket_urlpatterns = [
#     re_path(r'ws/socket-server', consumer.ChatConsumer.as_asgi()),
# ]

application = ProtocolTypeRouter({
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter([
                path('private_chat/<room_id>', ChatConsumer),
            ])
        )
    )
})