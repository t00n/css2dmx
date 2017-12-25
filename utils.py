from datetime import datetime
from time import sleep


def trange(start=None, end=None, interval=1):
    now = datetime.now().timestamp()
    if start is None:
        start = now
    else:
        start = start.timestamp()
    if end is not None:
        end = end.timestamp()
    if start > now:
        sleep(start - now)
    now = start
    i = 1
    while end is None or now < end:
        yield datetime.now()
        now = datetime.now().timestamp()
        target = start + i * interval
        if target > now:
            sleep(target - now)
            now = target
        i += 1
