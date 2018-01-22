from datetime import datetime

from hardware import parse_hw_file
from tree import parse_tree_file
from css import parse_css_file, parse_rgb, parse_transition, parse_animation
from utils import trange, compute_cubic_bezier, de_casteljau


def apply_style(tree, css):
    for rule in css.rules:
        for selector in rule.selectors:
            for node in tree.select(selector):
                for prop in rule.properties:
                    node.add_style(prop.name, prop.value)


DEFAULT_STYLES = {
    'color': [0, 0, 0]
}


def get_default_style(prop):
    return DEFAULT_STYLES[prop]


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


def compute_transition_function_at(transition, t):
    p1, p2 = get_bezier_coefs(transition.function)
    coefs = (0, 0), p1, p2, (1, 1)
    x0 = min(1, t / transition.duration)
    x = compute_cubic_bezier(p1[0], p2[0], x0)[-1]
    y = de_casteljau(x, coefs)[1]
    return y


def compute_prop_with_ratio(src, target, ratio):
    return [int(src[i] + (target[i] - src[i]) * ratio) for i in range(len(src))]


def compute_style(node, t):
    style = {}
    for prop in node.style:
        if 'transition' in node.style and prop in node.style['transition']:
            src = get_default_style(prop)
            target = node.style[prop]
            ratio = compute_transition_function_at(node.style['transition'][prop], t)
            value = compute_prop_with_ratio(src, target, ratio)
        else:
            value = node.style[prop]
        style[prop] = value
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


def send_dmx(state):
    print(state)


def run(hw, tree, css):
    apply_style(tree, css)
    tree.print()
    old_state = None
    now = datetime.now()
    for t in trange(interval=0.01):
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
