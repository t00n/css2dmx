from datetime import datetime
from functools import lru_cache
import serial
from time import sleep
import array

import ola.ClientWrapper

from lib.core import apply_style_on_dom, compute_dmx
from lib.hardware import load_devices
from lib.tree import parse_tree_file
from lib.css import parse_css_file
from lib.utils import trange


@lru_cache(maxsize=1)
def get_ola_client():
    try:
        return ola.ClientWrapper.OlaClient()
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
    client = get_ola_client()
    if client:
        bs = create_bytes(state)
        client.SendDmx(universe=1, data=array.array('B', bs))


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


def run(devices, tree, css, verbose=False):
    apply_style_on_dom(tree, css)
    tree.print()
    keyframes = css.keyframes
    old_state = None
    now = datetime.now()
    for t in trange(interval=0.02):
        state = compute_dmx(tree, devices, keyframes, t.timestamp() - now.timestamp())
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
    tree_file = os.path.join(dir_path, "tree.xml")
    css_file = os.path.join(dir_path, "style.css")

    verbose = len(sys.argv) == 3 and sys.argv[2] == "-v"

    devices = load_devices()
    tree = parse_tree_file(tree_file)
    css = parse_css_file(css_file)

    run(devices, tree, css, verbose)
