import typing as t


from functools import wraps
import signal


__all__ = [
    'timeout_decorator',
    'catch_exception_decorator'
]


def timeout_decorator(seconds: int = 10, error_message: t.Optional[t.Text] = "Timed Out!") -> t.Callable:
    def decorator(func: t.Callable) -> t.Callable:
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wrapper

    return decorator


def catch_exception_decorator(
        func: t.Callable, callback: t.Callable, exceptions: t.List[t.Type[Exception]] = None, default: t.Any = None
) -> t.Callable:
    if exceptions is None:
        exceptions = [Exception]

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except exceptions as e:
            callback(e)
            return default
    return wrapper
