class FailedTryRequest(Exception):
    """Raised when all attempts in the _try_request function have failed."""
    pass
