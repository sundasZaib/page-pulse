import asyncio
import time
from urllib.parse import urljoin

import httpx

from app.exceptions.fetch_exceptions import (
    ConnectionFailedError,
    FetchTimeoutError,
)
from app.security.url_validator import validate_url


MAX_CONCURRENT_FETCHES = 10

fetch_semaphore = asyncio.Semaphore(MAX_CONCURRENT_FETCHES)


class FetchResult:
    def __init__(
        self,
        status_code: int,
        response_time_ms: float,
        content_type: str | None,
        content_length: int,
    ):
        self.status_code = status_code
        self.response_time_ms = response_time_ms
        self.content_type = content_type
        self.content_length = content_length


async def fetch_url(url: str) -> FetchResult:
    # Validate the initial URL before acquiring a network slot
    validate_url(url)

    timeout = httpx.Timeout(
        connect=5.0,
        read=10.0,
        write=5.0,
        pool=5.0,
    )

    start_time = time.perf_counter()

    async with fetch_semaphore:
        async with httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=False,
        ) as client:

            current_url = url

            # Allow a maximum of 5 redirects
            for _ in range(5):

                try:
                    response = await client.get(current_url)

                except httpx.TimeoutException as exc:
                    raise FetchTimeoutError(
                        "The target URL took too long to respond."
                    ) from exc

                except httpx.RequestError as exc:
                    raise ConnectionFailedError(
                        "Unable to connect to the target website."
                    ) from exc

                # Stop if this is not a redirect
                if response.status_code not in {
                    301,
                    302,
                    303,
                    307,
                    308,
                }:
                    break

                location = response.headers.get("location")

                # Redirect response without a location header
                if not location:
                    break

                # Convert relative redirect URL to absolute URL
                next_url = urljoin(current_url, location)

                # Validate redirect destination before following it
                validate_url(next_url)

                current_url = next_url

            else:
                raise ValueError("Too many redirects")

    response_time_ms = round(
        (time.perf_counter() - start_time) * 1000,
        2,
    )

    return FetchResult(
        status_code=response.status_code,
        response_time_ms=response_time_ms,
        content_type=response.headers.get("content-type"),
        content_length=len(response.content),
    )