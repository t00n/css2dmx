from .utils import compute_cubic_bezier, de_casteljau
from .css import get_timing_function_coefs


def apply_style_on_dom(tree, css):
    for rule in css.rules:
        for selector in rule.selectors:
            for node in tree.select(selector):
                for prop in rule.properties:
                    node.add_style(prop.name, prop.value)


def compute_dmx_value(css_value, attr_desc, offset):
    address = attr_desc['chan'] + offset
    if 'enum' in attr_desc:
        dmx_value = attr_desc['enum'][css_value][0]
    else:
        attr_range = attr_desc.get('range', [0, 255])
        dmx_value = int(attr_range[0] + (attr_range[1] - attr_range[0]) * css_value / 255)
    return (address, dmx_value)


def compute_dmx_color(color, device, offset):
    res = []
    if color.name != '':
        res.append(compute_dmx_value(color.name, device['color']['name'], offset))
    else:
        res.append(compute_dmx_value(color.red, device['color']['red'], offset))
        res.append(compute_dmx_value(color.green, device['color']['green'], offset))
        res.append(compute_dmx_value(color.blue, device['color']['blue'], offset))
        if 'white' in device['color']:
            res.append(compute_dmx_value(color.white, device['color']['white'], offset))
        if 'alpha' in device['color']:
            res.append(compute_dmx_value(color.alpha, device['color']['alpha'], offset))
    return res


def compute_dmx_strobe(strobe, device, offset):
    res = []
    res.append(compute_dmx_value(strobe.speed, device['strobe']['speed'], offset))
    return res


def compute_dmx_pulse(pulse, device, offset):
    res = []
    direction, speed = pulse.direction, pulse.speed
    res.append(compute_dmx_value(direction, device['pulse']['direction'], offset))
    res.append(compute_dmx_value(speed, device['pulse']['speed'], offset))
    return res


def compute_dmx_auto(auto, device, offset):
    res = []
    name, speed = auto.name, auto.speed
    res.append(compute_dmx_value(name, device['auto']['name'], offset))
    if 'speed' in device['auto']:
        res.append(compute_dmx_value(speed, device['auto']['speed'], offset))
    return res


def compute_dmx_rotation(rotation, device, offset):
    res = []
    mode, position, speed = rotation.mode, rotation.position, rotation.speed
    if mode == 'manual':
        res.append(compute_dmx_value(position, device['rotation']['position'], offset))
    elif mode == 'auto':
        res.append(compute_dmx_value(speed, device['rotation']['speed'], offset))
    return res


COMPUTING_FUNCTIONS = {
    'color': compute_dmx_color,
    'strobe': compute_dmx_strobe,
    'pulse': compute_dmx_pulse,
    'auto': compute_dmx_auto,
    'rotation': compute_dmx_rotation
}


def compute_dmx(tree, devices, keyframes, t):
    dmx = []
    for node in tree.walk():
        if node.tag in devices:
            style = compute_style(node, keyframes, t)
            for prop, attrs in style.items():
                if prop in devices[node.tag] and prop in COMPUTING_FUNCTIONS:
                    dmx_val = COMPUTING_FUNCTIONS[prop](attrs, devices[node.tag], node.offset)
                    dmx.extend(dmx_val)
    return sorted(dmx, key=lambda x: x[0])


# ANIMATIONS
def animation_is_reversed(anim, t):
    anim_reversed = False
    if anim.direction == 'reverse':
        anim_reversed = True
    elif anim.direction == 'alternate':
        position = (t % (anim.duration * 2)) / anim.duration
        if position > 1:
            anim_reversed = True
    elif anim.direction == 'alternate-reverse':
        position = (t % (anim.duration * 2)) / anim.duration
        if position <= 1:
            anim_reversed = True
    return anim_reversed


def animation_is_on(anim, t):
    return anim.iteration == 'infinite' or t <= anim.duration * anim.iteration


def select_keyframe(frames, t):
    for f in frames:
        if f.selector / 100 > t:
            higher = f
            break
        lower = f
    return lower, higher


def compute_function_at(function, lower_frame, higher_frame, t):
    lower_selector, higher_selector = lower_frame.selector / 100, higher_frame.selector / 100
    x0 = (t - lower_selector) / (higher_selector - lower_selector)
    p1, p2 = get_timing_function_coefs(function)
    coefs = (0, 0), p1, p2, (1, 1)
    x = compute_cubic_bezier(p1[0], p2[0], x0)[-1]
    ratio = de_casteljau(x, coefs)[1]
    return ratio


def compute_animations(animations, keyframes, t):
    style = {}
    for name, anim in animations.items():
        # if positive delay, we don't start yet
        if t < anim.delay:
            continue
        # when delay is positive, we want to play the animation as if we are in the past
        # when delay is negative, we want to play the animation as if it had already begun
        anim_t = t - anim.delay
        anim_reversed = animation_is_reversed(anim, anim_t)
        if anim_reversed:
            anim_t = anim.duration - (anim_t % anim.duration)
        if animation_is_on(anim, anim_t):
            # compute where we are in the animation
            percent_t = (anim_t % anim.duration) / anim.duration
            # select the frame we're in
            lower_frame, higher_frame = select_keyframe(keyframes[name].frames, percent_t)
            # compute the bezier
            ratio = compute_function_at(anim.function, lower_frame, higher_frame, percent_t)
            # apply each property
            for low_prop in lower_frame.properties:
                for high_prop in higher_frame.properties:
                    if low_prop.name == high_prop.name:
                        style[low_prop.name] = low_prop.value.interpolate(high_prop.value, ratio)
    return style


def compute_style(node, keyframes, t):
    style = {}
    for prop in node.style:
        if prop == 'animation':
            props_animation = compute_animations(node.style[prop], keyframes, t)
            for name, value in props_animation.items():
                style[name] = value
        else:
            style[prop] = node.style[prop]
    return style
