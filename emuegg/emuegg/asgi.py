"""
ASGI config for emuegg project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os
from typing import Protocol

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator, OriginValidator
import base.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emuegg.settings')

application = ProtocolTypeRouter({ 
    'http' : get_asgi_application(),
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                base.routing.websocket_urlpatterns
            )
        )
    )
})
