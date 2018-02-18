from collections import namedtuple
import re

import cssutils
import tinycss2


DEFAULT_STYLES = {
    'color': [0, 0, 0]
}


def get_default_style(prop):
    return DEFAULT_STYLES[prop]


def parse_rgb(rgb):
    return [int(x.strip()) for x in rgb.split("rgb(")[1].split(")")[0].split(",")]


def parse_rgba(rgba):
    splitted = [x.strip() for x in rgba.split("rgba(")[1].split(")")[0].split(",")]
    return [int(x) for x in splitted[:3]] + [int(float(splitted[3]) * 255)]


def parse_color(color):
    if color[:4] == "rgba":
        return parse_rgba(color)
    elif color[:3] == "rgb":
        return parse_rgb(color)
    else:
        raise Exception("Expected a color, got {}".format(color))


def parse_time(duration):
    if duration[-2:] == 'ms':
        return float(duration[:-2]) / 1000
    elif duration[-1] == 's':
        return float(duration[:-1])
    else:
        raise Exception("Expected a duration, got {}".format(duration))


def parse_angle(angle):
    if angle[-3:] == 'deg':
        return float(angle[:-3])
    else:
        raise Exception("Expected an angle, got {}".format(angle))


Function = namedtuple('Function', ['name', 'params'])

TIMING_FUNCTIONS = ["ease", "linear", "ease-in", "ease-out", "ease-in-out", "cubic-bezier"]


def parse_timing_function(function):
    match = re.match(r'\A([a-zA-Z-]+)(\(\w+(?:, \w+)*\))?\Z', function)
    groups = match.groups()
    if groups[0] is not None and groups[0] in TIMING_FUNCTIONS:
        name = groups[0]
        params = [float(x.strip()) for x in groups[1][1:-1].split(',')] if groups[1] is not None else []
        return Function(name=name, params=params)
    else:
        raise Exception("Expected timing function, got '{}'".format(function))


def parse_iteration_count(iteration):
    if iteration == 'infinite':
        return iteration
    else:
        try:
            return int(iteration)
        except ValueError:
            raise Exception("Expected a number or 'infinite' for iteration-count, got {}".format(iteration))

DIRECTIONS = ['normal', 'reverse', 'alternate', 'alternate-reverse']


def parse_direction(direction):
    if direction in DIRECTIONS:
        return direction
    else:
        raise Exception("Expected direction, got '{}'".format(direction))


Transition = namedtuple('Transition', ['duration', 'function'])


def parse_transition(transition):
    transitions = {}
    # e.g. "transition: color 5s"
    # e.g. "transition: color 0.5s linear"
    match = re.match(r'(\w+) (\d+(?:\.\d+)?m?s)(?: (.+))?', transition)
    groups = match.groups()
    if groups[0] is not None:
        target_prop = groups[0]
        if groups[1] is not None:
            duration = parse_time(groups[1])
        else:
            duration = 0
        function = parse_timing_function(groups[2]) if groups[2] is not None else 'ease'
        transitions[target_prop] = Transition(duration=duration, function=function)
    return transitions

Animation = namedtuple('Animation', ['duration', 'function', 'delay', 'iteration', 'direction'])


def parse_animation(animation):
    animations = {}
    # e.g. "red2green 5s ease 0s infinite alternate"
    match = re.match(r'(\w+) (\d+m?s) (.+) (\d+m?s) (.+) (.+)', animation)
    groups = match.groups()
    if groups[0] is not None:
        target_prop = groups[0]
        duration = parse_time(groups[1]) if groups[1] is not None else 0
        function = parse_timing_function(groups[2]) if groups[2] is not None else 'ease'
        delay = parse_time(groups[3]) if groups[3] is not None else 0
        iteration = parse_iteration_count(groups[4]) if groups[4] is not None else 1
        direction = parse_direction(groups[5]) if groups[5] is not None else 'normal'
        animations[target_prop] = Animation(duration=duration,
                                            function=function,
                                            delay=delay,
                                            iteration=iteration,
                                            direction=direction)
    return animations


CSS = namedtuple('CSS', ['rules', 'keyframes'])
Rule = namedtuple('Rule', ['selectors', 'properties'])
Selector = namedtuple('Selector', ['type', 'value'])
Property = namedtuple('Property', ['name', 'value'])

IMPLEMENTED_PROPERTIES = ['color', 'animation']


def parse_properties(style):
    properties = []
    for prop in IMPLEMENTED_PROPERTIES:
        if prop in style:
            if prop == "color":
                val = parse_color(style[prop])
            elif prop == "animation":
                val = parse_animation(style[prop])
            properties.append(Property(name=prop, value=val))
    return properties


def parse_rules(css):
    rules = []
    for r in css.cssRules:
        if r.type == 1:  # style rule
            selectors = []
            for s in r.selectorList:
                if s.selectorText[0] == "#":
                    typ = 'id'
                elif s.selectorText[0] == '.':
                    typ = 'class'
                else:
                    raise NotImplementedError("'{}' selector type is not implemented".format(s.selectorText))
                value = s.selectorText[1:]
                selectors.append(Selector(type=typ, value=value))
            properties = parse_properties(r.style)
            rules.append(Rule(selectors=selectors, properties=properties))
    return rules

KeyframeRule = namedtuple('KeyframeRule', ['name', 'frames'])
Keyframe = namedtuple('Keyframe', ['selector', 'properties'])


def parse_keyframe_name(prelude):
    idents = [token for token in prelude if token.type == 'ident']
    if len(idents) != 1:
        raise Exception("Expected exactly one identifier for keyframe, got '{}'".format(prelude))
    return idents[0].lower_value


def parse_keyframe_frames(content):
    frames = []
    content = [token for token in content if token.type != 'whitespace']
    # goal : alternate between percentage and commas until we come across a rule
    # we register this rule for all the percentages encountered and reset percentages
    is_percentage = True
    percentages = []
    for token in content:
        if is_percentage:
            if token.type == 'percentage':
                percentages.append(token.int_value)
                is_percentage = False
            else:
                raise Exception("Expected percentage in keyframe, got '{}'".format(token))
        else:
            # when we encounter a comma, next token must be a percentage
            if token.type == 'literal' and token.value == ',':
                is_percentage = True
            elif token.type == '{} block':
                style = cssutils.parseStyle(" ".join([x.serialize() for x in token.content]))
                properties = parse_properties(style)
                for perc in percentages:
                    frames.append(Keyframe(selector=perc, properties=properties))
                percentages = []
                is_percentage = True
            else:
                raise Exception("Expected comma or curly-braces block, got'{}'".format(token))
    return sorted(frames, key=lambda f: f.selector)


def parse_keyframes(css):
    keyframes = {}
    for r in css:
        if r.type == 'at-rule' and r.at_keyword == 'keyframes':
            name = parse_keyframe_name(r.prelude)
            frames = parse_keyframe_frames(r.content)
            keyframes[name] = KeyframeRule(name=name, frames=frames)
    return keyframes


def parse_css_file(filename):
    css = cssutils.parseFile(filename)
    rules = parse_rules(css)
    with open(filename) as f:
        css = tinycss2.parse_stylesheet(f.read())
    keyframes = parse_keyframes(css)
    return CSS(rules=rules, keyframes=keyframes)

if __name__ == '__main__':
    res = parse_css_file("yolo.css")
    print(res)
