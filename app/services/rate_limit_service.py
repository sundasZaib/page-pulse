import time


RATE_LIMIT = 60
RATE_WINDOW_SECONDS = 60


_client_requests: dict[str, list[float]] = {}


def check_rate_limit(client_id: str) -> bool:
    now = time.time()
    window_start = now - RATE_WINDOW_SECONDS

    timestamps = _client_requests.get(client_id, [])

    # Keep only requests from the current window
    timestamps = [
        timestamp
        for timestamp in timestamps
        if timestamp > window_start
    ]

    if len(timestamps) >= RATE_LIMIT:
        _client_requests[client_id] = timestamps
        return False

    timestamps.append(now)
    _client_requests[client_id] = timestamps

    return True