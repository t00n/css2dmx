from datetime import datetime
import socket
from functools import lru_cache
import serial
from time import sleep

from lib.hardware import parse_hw_file
from lib.tree import parse_tree_file
from lib.css import parse_css_file
from lib.utils import trange, compute_cubic_bezier, de_casteljau


@lru_cache(maxsize=1)
def get_socket():
    try:
        sock = socket.create_connection(("127.0.0.1", 9010))
        return sock
    except Exception as e:
        print(e)
        return None


@lru_cache(maxsize=1)
def get_serial():
    try:
        return serial.Serial("/dev/ttyACM0", 115200, timeout=.1)
    except serial.serialutil.SerialException as e:
        print(e)
        return None


def apply_style(tree, css):
    for rule in css.rules:
        for selector in rule.selectors:
            for node in tree.select(selector):
                for prop in rule.properties:
                    node.add_style(prop.name, prop.value)


def get_bezier_coefs(function):
    if function.name == 'ease':
        p1, p2 = (0.25, 0.1), (0.25, 1)
    elif function.name == 'ease-in':
        p1, p2 = (0.42, 0), (1, 1)
    elif function.name == 'ease-out':
        p1, p2 = (0, 0), (0.58, 1)
    elif function.name == 'ease-in-out':
        p1, p2 = (0.42, 0), (0.58, 1)
    elif function.name == 'linear':
        p1, p2 = (0, 0), (1, 1)
    elif function.name == 'cubic-bezier':
        p1, p2 = (function.params[0], function.params[1]), (function.params[2], function.params[3])
    return p1, p2


def compute_prop_with_ratio(src, target, ratio):
    return [int(src[i] + (target[i] - src[i]) * ratio) for i in range(len(src))]


def compute_animations(animations, keyframes, t):
    style = {}
    for name, anim in animations.items():
        if anim.iteration == 'infinite' or t <= anim.duration * anim.iteration:
            # compute where we are in the animation
            percent_t = (t % anim.duration) / anim.duration
            # select the frame we're in
            frames = keyframes[name].frames
            for f in frames:
                selector = f.selector / 100
                if selector > percent_t:
                    higher_selector = selector
                    higher_properties = f.properties
                    break
                lower_selector = selector
                lower_properties = f.properties
            x0 = (percent_t - lower_selector) / (higher_selector - lower_selector)
            p1, p2 = get_bezier_coefs(anim.function)
            coefs = (0, 0), p1, p2, (1, 1)
            x = compute_cubic_bezier(p1[0], p2[0], x0)[-1]
            y = de_casteljau(x, coefs)[1]
            for low_prop in lower_properties:
                for high_prop in higher_properties:
                    if low_prop.name == high_prop.name:
                        value = compute_prop_with_ratio(low_prop.value, high_prop.value, y)
                        style[low_prop.name] = value
    return style


def compute_style(node, keyframes, t):
    style = {}
    for prop in node.style:
        if prop == 'animation':
            props_animation = compute_animations(node.style[prop], keyframes, t)
            for name, value in props_animation.items():
                style[name] = value
        else:
            value = node.style[prop]
        style[prop] = value
    return style


def compute_dmx(tree, hw, keyframes, t):
    dmx = []
    for node in tree.walk():
        if node.id in hw:
            style = compute_style(node, keyframes, t)
            for prop, val in style.items():
                if prop in hw[node.id]:
                    dmx.extend(list(zip(hw[node.id][prop], val)))
    return sorted(dmx, key=lambda x: x[0])


@lru_cache()
def create_bytes(state):
    state = dict(state)
    bs = []
    for i in range(1, 512):
        bs.append(state.get(i, 0))
    bs = bytes(bs)
    return bs


def send_ola(state):
    sock = get_socket()
    if sock:
        bs = create_bytes(state)
        sock.send(b"\35\2\0\20")
        sock.send(b"\10\n\20\0\32\rStreamDmxData\"\207\4\10\1\22\200\4" +
                  bs +
                  b"\0\30d")


def send_serial(state):
    ser = get_serial()
    if ser:
        bs = b"\x00" + create_bytes(state)
        for i in range(8):
            chunk = bs[i * 16:(i + 1) * 16]
            ser.write(chunk)
            sleep(1e-4)


def send_dmx(state):
    state = tuple(state)
    send_ola(state)
    send_serial(state)


def run(hw, tree, css, verbose=False):
    apply_style(tree, css)
    tree.print()
    keyframes = css.keyframes
    old_state = None
    now = datetime.now()
    for t in trange(interval=0.02):
        state = compute_dmx(tree, hw, keyframes, t.timestamp() - now.timestamp())
        if state != old_state:
            old_state = state
            send_dmx(state)
            if verbose:
                print(state)

if __name__ == '__main__':
    import sys
    import os
    dir_path = sys.argv[1]
    dir_name = os.path.basename(dir_path)
    hw_file = os.path.join(dir_path, dir_name + ".hw")
    tree_file = os.path.join(dir_path, dir_name + ".tree")
    css_file = os.path.join(dir_path, dir_name + ".css")

    verbose = len(sys.argv) == 3 and sys.argv[2] == "-v"

    hw = parse_hw_file(hw_file)
    tree = parse_tree_file(tree_file)
    css = parse_css_file(css_file)

    run(hw, tree, css, verbose)
