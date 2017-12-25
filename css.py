import cssutils
from collections import namedtuple

Transition = namedtuple('Transition', ['duration', 'function'])


def parse_rgb(rgb):
    return [int(x.strip()) for x in rgb.split("rgb(")[1].split(")")[0].split(",")]


def parse_duration(duration):
    if duration[-2:] == 'ms':
        return float(duration[:-2]) / 1000
    elif duration[-1] == 's':
        return float(duration[:-1])


def parse_transitions(style):
    transitions = {}
    for prop in style:
        if prop == "transition":
            # e.g. "transition: color 5s"
            # e.g. "transition: color 0.5s linear"
            values = style[prop].split(" ")
            if len(values) >= 1:
                target_prop = values[0]
                if len(values) >= 2:
                    duration = parse_duration(values[1])
                else:
                    duration = 0
                if len(values) >= 3:
                    function = values[2]
                else:
                    function = 'ease'
                transitions[target_prop] = Transition(duration=duration, function=function)
    return transitions


def parse_css_file(filename):
    css = cssutils.parseFile(filename)
    return css

if __name__ == '__main__':
    res = parse_css_file("yolo.css")
    print(res)
