import signal
from contextlib import contextmanager


class TimeoutException(Exception): pass


def time_limit(func):
    @contextmanager
    def _time_limit(seconds):
        def signal_handler(signum, frame):
            raise TimeoutException("Timed out!")
        signal.signal(signal.SIGALRM, signal_handler)
        signal.alarm(seconds)
        try:
            yield
        finally:
            signal.alarm(0)

    def _run(*args, **kwargs):
        try:
            with _time_limit(seconds=10):
                res = func(*args, **kwargs)
        except TimeoutException:
            print('time out 10s')
    return _run



