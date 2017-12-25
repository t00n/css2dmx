import cssutils


def get_css_style(css, id=None, klass=None):
    if id is not None:
        for rule in css.cssRules:
            if rule.type == 1 and rule.selectorText[0] == "#" and rule.selectorText[1:] == id:
                return rule.style
    elif klass is not None:
        for rule in css.cssRules:
            if rule.type == 1 and rule.selectorText[0] == "." and rule.selectorText[1:] == klass:
                return rule.style
    return []


def parse_css_file(filename):
    css = cssutils.parseFile(filename)
    return css

if __name__ == '__main__':
    res = parse_css_file("yolo.css")
    print(res)
