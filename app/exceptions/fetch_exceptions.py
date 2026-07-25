class FetchError(Exception):
    """Base fetch exception."""
    pass


class FetchTimeoutError(FetchError):
    pass


class ConnectionFailedError(FetchError):
    pass


class InvalidTargetError(FetchError):
    pass