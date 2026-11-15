"""Explicit allowlisted, read-only service connectors.

Each connector is a user-configured HTTPS endpoint. Credentials are read from
environment variables only. Never pass secrets through the model prompt.
"""
import ipaddress
import os
import socket
from urllib.parse import urlparse

import requests


class IntegrationError(Exception):
    pass


def _validate_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise IntegrationError("Only credential-free HTTPS URLs are permitted")
    if parsed.port not in (None, 443):
        raise IntegrationError("Only standard HTTPS port is permitted")
    host = parsed.hostname
    try:
        addresses = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    except OSError as exc:
        raise IntegrationError("Hostname cannot be resolved") from exc
    if not addresses or any(
        not ipaddress.ip_address(addr[4][0]).is_global for addr in addresses
    ):
        raise IntegrationError("Private or non-global network destinations are prohibited")


def available_connectors() -> list[str]:
    raw = os.getenv("ANGEL_CONNECTORS", "")
    return sorted({name.strip() for name in raw.split(",") if name.strip() and name.strip().isidentifier()})


def read_connector(name: str) -> dict:
    if name not in available_connectors():
        raise IntegrationError("Connector is not enabled")
    prefix = f"ANGEL_CONNECTOR_{name.upper()}_"
    url = os.getenv(prefix + "URL", "")
    token = os.getenv(prefix + "TOKEN", "")
    if not url:
        raise IntegrationError("Connector URL not configured")
    _validate_url(url)
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    try:
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=False)
        response.raise_for_status()
        if len(response.content) > 64_000:
            raise IntegrationError("Connector response too large")
        return {"connector": name, "status": response.status_code, "data": response.text[:8000]}
    except requests.RequestException as exc:
        raise IntegrationError("Connector request failed") from exc
