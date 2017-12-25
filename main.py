from datetime import datetime, timedelta

from hardware import parse_hw_file
from tree import parse_tree_file
from css import parse_css_file, parse_rgb, parse_transitions
from utils import trange


def apply_style(tree, css):
    for rule in css.cssRules:
        for selector in rule.selectorList:
            for node in tree.select(selector.selectorText):
                for prop in rule.style:
                    node.add_style(prop.name, prop.value)


def lerp(t, a, b):
    return t * b + (1 - t) * a


def lerpP(t, zero, one):
    return lerp(t, zero[0], one[0]), lerp(t, zero[1], one[1])


def de_casteljau(t, coefs):
    if len(coefs) == 1:
        return coefs[0]
    else:
        return de_casteljau(t, [lerpP(t, x, y) for x, y in zip(coefs[:-1], coefs[1:])])


def cubic_bezier(x0, coefs):
    for t in range(0, 250, 1):
        t = t / 250
        x, y = de_casteljau(t, coefs)
        if abs(x - x0) < 0.01:
            return x, y
    return 1, 1


def compute_transition_function_at(transition, t):
    if transition.function == 'ease':
        p1, p2 = (0.25, 0.1), (0.25, 1)
    elif transition.function == 'ease-in':
        p1, p2 = (0.42, 0), (1, 1)
    elif transition.function == 'ease-out':
        p1, p2 = (0, 0), (0.58, 1)
    elif transition.function == 'ease-in-out':
        p1, p2 = (0.42, 0), (0.58, 1)
    elif transition.function == 'linear':
        p1, p2 = (0, 0), (1, 1)
    elif transition.function == 'cubic-bezier':
        p1, p2 = transition.params
    coefs = (0, 0), p1, p2, (1, 1)
    t /= transition.duration
    x, y = cubic_bezier(t, coefs)
    return y


def compute_color(color, ratio):
    return [max(0, min(255, int(ratio * x))) for x in color]


def compute_style(node, t):
    transitions = parse_transitions(node.style)
    style = {}
    for prop in node.style:
        if prop == "color":
            color = parse_rgb(node.style[prop])
            if prop in transitions:
                ratio = compute_transition_function_at(transitions[prop], t)
                color = compute_color(color, ratio)
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


def send_dmx(state):
    print(state)


def run(hw, tree, css):
    apply_style(tree, css)
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
