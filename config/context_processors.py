from django.conf import settings


def ws_port(request):
    return {"ws_port": getattr(settings, "WS_PORT", "8001")}
