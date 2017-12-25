from itertools import chain
from datetime import datetime
from time import sleep

from hardware import parse_hw_file
from tree import parse_tree_file
from css import parse_css_file, parse_rgb, parse_duration


def apply_style(tree, css):
    for rule in css.cssRules:
        for selector in rule.selectorList:
            for node in tree.select(selector.selectorText):
                for prop in rule.style:
                    node.add_style(prop.name, prop.value)


def compute_transitions(style):
    transitions = {}
    for prop in style:
        if prop == "transition":
            target_prop, duration = style[prop].split(" ")
            transitions[target_prop] = parse_duration(duration)
    return transitions


def compute_style(node, t):
    transitions = compute_transitions(node.style)
    style = {}
    for prop in node.style:
        if prop == "color":
            color = parse_rgb(node.style[prop])
            if prop in transitions:
                ratio = t / transitions[prop]
                color = [max(0, min(255, int(ratio * x))) for x in color]
            style["color"] = color
    return style


def compute_dmx(tree, hw, t):
    dmx = []
    for node in tree.walk():
        if node.id in hw:
            style = compute_style(node, t)
            for prop, val in style.items():
                if prop in hw[node.id]:
                    dmx.extend(list(zip(hw[node.id][prop], val)))
    return sorted(dmx, key=lambda x: x[0])


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


def send_dmx(state):
    print(state)


def run(hw, tree, css):
    apply_style(tree, css)
    old_state = None
    now = datetime.now()
    for t in trange(interval=0.1):
        state = compute_dmx(tree, hw, t.timestamp() - now.timestamp())
        if state != old_state:
            old_state = state
            send_dmx(state)

if __name__ == '__main__':
    import sys
    project = sys.argv[1]
    hw_file = project + ".hw"
    tree_file = project + ".tree"
    css_file = project + ".css"

    hw = parse_hw_file(hw_file)
    tree = parse_tree_file(tree_file)
    css = parse_css_file(css_file)

    run(hw, tree, css)
