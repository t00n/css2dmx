from datetime import datetime
from time import sleep
import math


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


def lerp(t, a, b):
    return t * b + (1 - t) * a


def lerpP(t, zero, one):
    return lerp(t, zero[0], one[0]), lerp(t, zero[1], one[1])


def de_casteljau(t, coefs):
    if len(coefs) == 1:
        return coefs[0]
    else:
        return de_casteljau(t, [lerpP(t, x, y) for x, y in zip(coefs[:-1], coefs[1:])])


def compute_roots_cubic(a, b, c, d):
    b /= a
    c /= a
    d /= a

    p = (3 * c - b ** 2) / 3
    q = (2 * b * b ** 2 - 9 * b * c + 27 * d) / 27

    if p == 0:
        return [math.pow(-q, 1 / 3)]
    elif q == 0:
        return [math.sqrt(-p), -math.sqrt(-p)]
    else:
        discriminant = math.pow(q / 2, 2) + math.pow(p / 3, 3)
        if discriminant == 0:
            return [math.pow(q / 2, 1 / 3) - b / 3]
        elif discriminant > 0:
            return [math.pow(-(q / 2) + math.sqrt(discriminant), 1 / 3) - math.pow((q / 2) + math.sqrt(discriminant), 1 / 3) - b / 3]
        else:
            r = math.sqrt(math.pow(-(p / 3), 3))
            phi = math.acos(-(q / (2 * math.sqrt(math.pow(-(p / 3), 3)))))
            s = 2 * math.pow(r, 1 / 3)
            return [
                s * math.cos(phi / 3) - b / 3,
                s * math.cos((phi + 2 * math.pi) / 3) - b / 3,
                s * math.cos((phi + 4 * math.pi) / 3) - b / 3
            ]


def compute_cubic_bezier(p1, p2, x0):
    p0 = -x0
    p1 -= x0
    p2 -= x0
    p3 = 1 - x0

    a = p3 - 3 * p2 + 3 * p1 - p0
    b = 3 * p2 - 6 * p1 + 3 * p0
    c = 3 * p1 - 3 * p0
    d = p0
    roots = compute_roots_cubic(a, b, c, d)
    return [r for r in roots if r >= 0 and r <= 1]
