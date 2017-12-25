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
            if len(groups) >= 1:
                target_prop = groups[0]
                if len(groups) >= 2:
                    duration = parse_duration(groups[1])
                else:
                    duration = 0
                params = []
                if len(groups) >= 5:
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


def parse_css_file(filename):
    css = cssutils.parseFile(filename)
    return css

if __name__ == '__main__':
    res = parse_css_file("yolo.css")
    print(res)
