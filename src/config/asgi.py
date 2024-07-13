"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application

asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from notifications.routing import websocket_urlpatterns as notifications_urlpatterns
from messenger.routing import websocket_urlpatterns as messenger_urlpatterns
from core.middleware import JWTAuthMiddleware

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = ProtocolTypeRouter(
    {
        "http": asgi_app,
        "websocket": AuthMiddlewareStack(
            JWTAuthMiddleware(
                URLRouter(notifications_urlpatterns + messenger_urlpatterns)
            )
        ),
    }
)
