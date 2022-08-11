import typing as t


from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from functools import wraps


__all__ = [
    'run_in_threadpool',
    'run_in_thread',
    'run_in_thread_decorator',
    'run_in_threadpool_decorator',
]


def run_in_threadpool(func: t.Callable, return_result: bool = False, *args, **kwargs) -> t.Optional[t.Any]:
    """
    Runs a function in a thread pool.

    :param func: The function to run
    :type func: t.Callable

    :param return_result: Whether to return the result
    :type return_result: bool

    :param args: The arguments to pass to the function
    :type args: t.Any

    :param kwargs: The keyword arguments to pass to the function
    :type kwargs: t.Any

    :return: None
    :rtype: None
    """

    if return_result:
        return ThreadPoolExecutor().submit(func, *args, **kwargs).result()

    ThreadPoolExecutor().submit(func, *args, **kwargs)


def run_in_thread(func: t.Callable, *args, **kwargs) -> None:
    """
    Runs a function in a thread.

    :param func: The function to run
    :type func: t.Callable

    :param args: The arguments to pass to the function
    :type args: t.Any

    :param kwargs: The keyword arguments to pass to the function
    :type kwargs: t.Any

    :return: None
    :rtype: None
    """

    Thread(target=func, args=args, kwargs=kwargs).start()


def run_in_thread_decorator(func: t.Callable) -> t.Callable:
    """
    Decorator to run a function in a thread.

    :param func: The function to run
    :type func: t.Callable

    :return: The decorated function
    :rtype: t.Callable
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        run_in_thread(func, *args, **kwargs)

    return wrapper


def run_in_threadpool_decorator(func: t.Callable) -> t.Callable:
    """
    Decorator to run a function in a thread pool.

    :param func: The function to run
    :type func: t.Callable

    :return: The decorated function
    :rtype: t.Callable
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        run_in_threadpool(func, *args, **kwargs)

    return wrapper
