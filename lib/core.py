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
    res.append(compute_dmx_value(color[0], device['color']['red'], offset))
    res.append(compute_dmx_value(color[1], device['color']['green'], offset))
    res.append(compute_dmx_value(color[2], device['color']['blue'], offset))
    if 'alpha' in device['color'] and len(color) == 4:
        res.append(compute_dmx_value(color[3], device['color']['alpha'], offset))
    return res


def compute_dmx_strobe(strobe, device, offset):
    res = []
    res.append(compute_dmx_value(strobe, device['strobe']['speed'], offset))
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


def compute_dmx(tree, devices, keyframes, t):
    dmx = []
    for node in tree.walk():
        if node.tag in devices:
            style = compute_style(node, keyframes, t)
            for prop, attrs in style.items():
                if prop in devices[node.tag]:
                    dmx_val = []
                    if prop == "color":
                        dmx_val = compute_dmx_color(attrs, devices[node.tag], node.offset)
                    elif prop == "strobe":
                        dmx_val = compute_dmx_strobe(attrs, devices[node.tag], node.offset)
                    elif prop == "pulse":
                        dmx_val = compute_dmx_pulse(attrs, devices[node.tag], node.offset)
                    elif prop == "auto":
                        dmx_val = compute_dmx_auto(attrs, devices[node.tag], node.offset)
                    elif prop == "rotation":
                        dmx_val = compute_dmx_rotation(attrs, devices[node.tag], node.offset)
                        (attrs, devices[node.tag], node.offset)
                    dmx.extend(dmx_val)
    return sorted(dmx, key=lambda x: x[0])


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
        anim_reversed = False
        if anim.direction == 'reverse':
            anim_reversed = True
        elif anim.direction == 'alternate':
            position = (real_t % (anim.duration * 2)) / anim.duration
            if position > 1:
                anim_reversed = True
        elif anim.direction == 'alternate-reverse':
            position = (real_t % (anim.duration * 2)) / anim.duration
            if position <= 1:
                anim_reversed = True
        if anim_reversed:
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
            p1, p2 = get_timing_function_coefs(anim.function)
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
