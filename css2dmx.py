from datetime import datetime
import socket
from functools import lru_cache
import serial
from time import sleep

from lib.core import apply_style, compute_dmx
from lib.hardware import parse_hw_file
from lib.tree import parse_tree_file
from lib.css import parse_css_file
from lib.utils import trange


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
