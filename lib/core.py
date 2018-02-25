from .utils import compute_cubic_bezier, de_casteljau


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
        # if positive delay, we don't start yet
        if t < anim.delay:
            continue
        # when delay is positive, we want to play the animation as if we are in the past
        # when delay is negative, we want to play the animation as if it had already begun
        real_t = t - anim.delay
        if anim.direction == 'reverse':
            real_t = anim.duration - (real_t % anim.duration)
        if anim.iteration == 'infinite' or real_t <= anim.duration * anim.iteration:
            # compute where we are in the animation
            percent_t = (real_t % anim.duration) / anim.duration
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
