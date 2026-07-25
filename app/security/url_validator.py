from urllib.parse import urlparse
import ipaddress
import socket


ALLOWED_SCHEMES = {"http", "https"}


def validate_url(url: str) -> str:
    parsed = urlparse(url)

    if parsed.scheme not in ALLOWED_SCHEMES:
        raise ValueError("Only HTTP and HTTPS URLs are allowed")

    if not parsed.hostname:
        raise ValueError("URL must contain a valid hostname")

    hostname = parsed.hostname.lower()

    if hostname in {"localhost", "localhost.localdomain"}:
        raise ValueError("Localhost URLs are not allowed")

    try:
        addresses = socket.getaddrinfo(
            hostname,
            None,
            socket.AF_UNSPEC,
            socket.SOCK_STREAM,
        )
    except socket.gaierror:
        raise ValueError("Unable to resolve hostname")

    for address in addresses:
        ip = address[4][0]
        ip_obj = ipaddress.ip_address(ip)

        if (
            ip_obj.is_private
            or ip_obj.is_loopback
            or ip_obj.is_link_local
            or ip_obj.is_reserved
            or ip_obj.is_multicast
        ):
            raise ValueError(
                "URLs pointing to private or internal networks are not allowed"
            )

    return url