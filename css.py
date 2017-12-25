import cssutils


def parse_rgb(rgb):
    return [int(x.strip()) for x in rgb.split("rgb(")[1].split(")")[0].split(",")]


def parse_duration(duration):
    if duration[-2:] == 'ms':
        return float(duration[:-2]) / 1000
    elif duration[-1] == 's':
        return float(duration[:-1])


def parse_css_file(filename):
    css = cssutils.parseFile(filename)
    return css

if __name__ == '__main__':
    res = parse_css_file("yolo.css")
    print(res)
