# connection.py
# ─────────────────────────────────────────────
# Single shared AngelOne connection.
# Import `get_connection()` anywhere — returns the
# same connected SmartConnect object every time.
# Re-login happens automatically if session expires.
# ─────────────────────────────────────────────

import os
import pyotp
import logging
from datetime import datetime

try:
    from SmartApi import SmartConnect
except ImportError:
    raise ImportError("Run: pip install smartapi-python pyotp python-dotenv")

logger = logging.getLogger(__name__)
logging.basicConfig(
    level  = logging.INFO,
    format = "%(asctime)s [%(levelname)s] %(message)s",
)

# ── Singleton state ───────────────────────────
_smart_api   = None
_last_login  = None
SESSION_HOURS = 7.5   # Re-login after this many hours


def _login() -> SmartConnect:
    """Create a new SmartConnect session and return it."""
    global _smart_api, _last_login

    api_key = os.environ.get("ANGEL_API_KEY")
    client_id = os.environ.get("ANGEL_CLIENT_ID")
    password = os.environ.get("ANGEL_PASSWORD")
    totp_key = os.environ.get("ANGEL_TOTP_KEY")
    
    missing = []
    
    if not api_key:
        missing.append("ANGEL_API_KEY")
    
    if not client_id:
        missing.append("ANGEL_CLIENT_ID")
    
    if not password:
        missing.append("ANGEL_PASSWORD")
    
    if not totp_key:
        missing.append("ANGEL_TOTP_KEY")
    
    if missing:
        raise ValueError(
            f"Missing credentials: {', '.join(missing)}"
        )

    totp = pyotp.TOTP(totp_key).now()
    obj  = SmartConnect(api_key=api_key)
    resp = obj.generateSession(
        clientCode = client_id,
        password   = password,
        totp       = totp,
    )

    if resp.get("status") is True or resp.get("status") == "true":
        _smart_api  = obj
        _last_login = datetime.now()
        logger.info(f"AngelOne connected at {_last_login.strftime('%H:%M:%S')}")
        return _smart_api
    else:
        raise ConnectionError(f"AngelOne login failed: {resp.get('message', 'Unknown error')}")


def get_connection() -> SmartConnect:
    """
    Return a live AngelOne SmartConnect object.
    Automatically logs in on first call.
    Automatically re-logs in if session is older than 7.5 hours.

    Usage:
        from connection import get_connection
        api = get_connection()
        resp = api.ltpData("NSE", "Nifty 50", "99926000")
    """
    global _smart_api, _last_login

    # First call — login
    if _smart_api is None:
        return _login()

    # Session expired — re-login
    if _last_login:
        elapsed = (datetime.now() - _last_login).total_seconds() / 3600
        if elapsed > SESSION_HOURS:
            logger.info(f"Session {elapsed:.1f}h old — reconnecting...")
            return _login()

    return _smart_api


# ── Quick connection test ─────────────────────
if __name__ == "__main__":
    api = get_connection()
    resp = api.ltpData("NSE", "Nifty 50", "99926000")
    print("Connection test:")
    print(f"  Status : {resp.get('status')}")
    print(f"  Nifty  : {resp.get('data', {}).get('ltp')}")
