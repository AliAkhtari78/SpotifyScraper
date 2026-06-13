"""Spotify's TOTP scheme for the ``/api/token`` handshake.

Exchanging an ``sp_dc`` cookie for a web-player access token requires a
time-based one-time password whose secret Spotify ships (obfuscated) in its
web-player bundle. The secrets rotate; refresh :data:`TOTP_SECRETS` from the
current bundle's ``eU`` array when ``totpVerExpired`` starts appearing (see
``scripts/refresh_totp.py``).
"""

from __future__ import annotations

import hashlib
import hmac
import struct

#: ``(version, secret)`` pairs, newest first. Spotify keeps a few grace versions
#: live at once; we try them newest-first during the token exchange.
TOTP_SECRETS: tuple[tuple[int, str], ...] = (
    (61, ',7/*F("rLJ2oxaKL^f+E1xvP@N'),
    (60, 'OmE{ZA.J^":0FG\\\\Uz?[@WW'),
    (59, "{iOFn;4}<1PFYKPV?5{%u14]M>/V0hDH"),
)

_PERIOD = 30
_DIGITS = 6


def totp_key(secret: str) -> bytes:
    """Derive the HMAC key from a Spotify TOTP secret string.

    Mirrors the web player: XOR each character code with ``index % 33 + 9``,
    join the decimal results, and UTF-8 encode them.
    """
    return "".join(str(ord(char) ^ (index % 33 + 9)) for index, char in enumerate(secret)).encode()


def generate(secret: str, timestamp_seconds: float) -> str:
    """Return the 6-digit TOTP for ``secret`` at ``timestamp_seconds``."""
    counter = int(timestamp_seconds) // _PERIOD
    digest = hmac.new(totp_key(secret), struct.pack(">Q", counter), hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    code = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
    return str(code % 10**_DIGITS).zfill(_DIGITS)
