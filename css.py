import cssutils
from collections import namedtuple
import re

Transition = namedtuple('Transition', ['duration', 'function', 'params'])


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


CSS = namedtuple('CSS', ['rules'])
Rule = namedtuple('Rule', ['selectors', 'properties'])
Selector = namedtuple('Selector', ['type', 'value'])
Property = namedtuple('Property', ['name', 'value'])

IMPLEMENTED_PROPERTIES = ['color', 'transition']


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
            properties = []
            for prop in IMPLEMENTED_PROPERTIES:
                if prop in r.style:
                    properties.append(Property(name=prop, value=r.style[prop]))
            rules.append(Rule(selectors=selectors, properties=properties))
    return rules


def parse_css_file(filename):
    css = cssutils.parseFile(filename)
    rules = parse_rules(css)
    return CSS(rules=rules)

if __name__ == '__main__':
    res = parse_css_file("yolo.css")
    print(res)
