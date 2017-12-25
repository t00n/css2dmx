from itertools import chain
from datetime import datetime
from time import sleep

from hardware import parse_hw_file
from tree import parse_tree_file, walk_tree
from css import parse_css_file, get_css_style


def parse_rgb(rgb):
    return [int(x.strip()) for x in rgb.split("rgb(")[1].split(")")[0].split(",")]


def color_to_dmx(color, hw):
    return list(zip(hw, color))


def transition_to_dmx(style):
    pass


def apply_style(tree, css):
    for id, node in walk_tree(tree):
        node['style'] = {}
        for style in chain(*[get_css_style(css, id=id), *[get_css_style(css, klass=k) for k in node.get('class', "").split(" ")]]):
            node['style'][style.name] = style.value


def compute_transitions(style):
    transitions = {}
    for s in style:
        if s == "transition":
            prop, duration = style[s].split(" ")
            transitions[prop] = float(duration[:-1])
    return transitions


def compute_dmx(tree, hw, t):
    dmx = []
    for id, node in walk_tree(tree):
        if id in hw:
            transitions = compute_transitions(node['style'])
            for style in node['style']:
                if style in hw[id]:
                    if style == "color":
                        color = parse_rgb(node['style'][style])
                        if style in transitions:
                            ratio = t / transitions[style]
                            color = [max(0, min(255, int(ratio * x))) for x in color]
                        dmx.extend(list(zip(hw[id][style], color)))
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


def write(state):
    print(state)


def run(hw, tree, css):
    apply_style(tree, css)
    old_state = None
    now = datetime.now()
    for t in trange(interval=0.1):
        state = compute_dmx(tree, hw, t.timestamp() - now.timestamp())
        if state != old_state:
            old_state = state
            write(state)

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
