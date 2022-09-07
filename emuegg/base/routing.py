from email.mime import application
import webbrowser
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator, OriginValidator
import base.routing
from django.urls import re_path
from . import consumer

websocket_urlpatterns = [
    re_path(r'ws/socket-server', consumer.ChatConsumer.as_asgi()),
]

# application = ProtocolTypeRouter({
#     'websocket': AllowedHostsOriginValidator(
#         AuthMiddlewareStack(
#             # URLRouter(
#             #     base.routing.websocket_urlpatterns
#             # )
#         )
#     )
# })