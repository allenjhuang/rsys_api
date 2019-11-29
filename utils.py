import logging
from typing import Any, Callable


def log_wrap(
    logging_func: Callable = logging.info,
    before_msg: str = "",
    after_msg: str = ""
) -> Any:
    """Wrapper that gives a function a start and end logging message.

    Parameters
    ----------
    logging_func : func
        Pointer to the logging function intended to be used.
    before_msg : str
        Message passed to logging before the primary function is called.
    after_msg : str
        Message passed to logging after the primary function is called.
    """
    def decorate(func):
        """ Decorator """
        def call(*args, **kwargs):
            """ Actual wrapping """
            if before_msg != "":
                logging_func(before_msg)
            result = func(*args, **kwargs)
            if after_msg != "":
                logging_func(after_msg)
            return result
        return call
    return decorate
