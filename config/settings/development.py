from .base import *
from pathlib import Path

SSL_CERTIFICATE = BASE_DIR / "certs" / "server.crt"
SSL_KEY = BASE_DIR / "certs" / "server.key"


# Expire the session cookie immediately when the user closes their browser/PWA window
SESSION_EXPIRE_AT_BROWSER_CLOSE = True