from collections import namedtuple
import re

import cssutils
import tinycss2


def parse_rgb(rgb):
    return [int(x.strip()) for x in rgb.split("rgb(")[1].split(")")[0].split(",")]


def parse_duration(duration):
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


Transition = namedtuple('Transition', ['duration', 'function', 'params'])


def parse_transitions(style):
    transitions = {}
    for prop in style:
        if prop == "transition":
            # e.g. "transition: color 5s"
            # e.g. "transition: color 0.5s linear"
            match = re.match(r'([\w-]*) (\d+(s|ms))( (.*))?', style[prop])
            groups = match.groups()
            if groups[0] is not None:
                target_prop = groups[0]
                if groups[1] is not None:
                    duration = parse_duration(groups[1])
                else:
                    duration = 0
                params = []
                if groups[4] is not None:
                    if not groups[4].startswith('cubic-bezier'):
                        function = groups[4]
                    else:
                        function = 'cubic-bezier'
                        params = [float(x.strip()) for x in groups[4].split('(')[1].split(')')[0].split(',')]
                        params = [[params[0], params[1]], [params[2], params[3]]]
                else:
                    function = 'ease'
                transitions[target_prop] = Transition(duration=duration, function=function, params=params)
    return transitions


CSS = namedtuple('CSS', ['rules', 'keyframes'])
Rule = namedtuple('Rule', ['selectors', 'properties'])
Selector = namedtuple('Selector', ['type', 'value'])
Property = namedtuple('Property', ['name', 'value'])

IMPLEMENTED_PROPERTIES = ['color', 'transition']


def parse_properties(style):
    properties = []
    for prop in IMPLEMENTED_PROPERTIES:
        if prop in style:
            properties.append(Property(name=prop, value=style[prop]))
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
    return frames


def parse_keyframes(css):
    keyframes = []
    for r in css:
        if r.type == 'at-rule' and r.at_keyword == 'keyframes':
            name = parse_keyframe_name(r.prelude)
            frames = parse_keyframe_frames(r.content)
            keyframes.append(KeyframeRule(name=name, frames=frames))
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
