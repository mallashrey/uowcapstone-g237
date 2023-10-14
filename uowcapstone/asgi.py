"""
ASGI config for uowcapstone project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import capstone.routing

from django.urls import path
from capstone.consumers import *


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uowcapstone.settings')

# application = get_asgi_application()
application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            capstone.routing.websocket_urlpatterns
        )
    )
})

# ws_patterns = [
#     path('ws/test/', TestConsumer)
# ]

# application = ProtocolTypeRouter({
#     'websocket': URLRouter(ws_patterns)
# })
