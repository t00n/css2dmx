from itertools import chain

from hardware import parse_hw_file
from tree import parse_tree_file, walk_tree
from css import parse_css_file, get_css_style


def rgb_to_dmx(style, hw):
    rgb = [int(x.strip()) for x in style.split("rgb(")[1].split(")")[0].split(",")]
    return list(zip(hw, rgb))


def apply_style(tree, css):
    for id, node in walk_tree(tree):
        node['style'] = {}
        for style in chain(*[get_css_style(css, id=id), *[get_css_style(css, klass=k) for k in node.get('class', "").split(" ")]]):
            node['style'][style.name] = style.value


def compute_dmx(tree, hw):
    dmx = []
    for id, node in walk_tree(tree):
        if id in hw:
            for style in node['style']:
                if style in hw[id]:
                    if style == "color":
                        dmx.extend(rgb_to_dmx(node['style'][style], hw[id][style]))
    return sorted(dmx, key=lambda x: x[0])


def run(hw, tree, css):
    apply_style(tree, css)
    print(tree)
    dmx = compute_dmx(tree, hw)
    print(dmx)

if __name__ == '__main__':
    import sys
    project = sys.argv[1]
    hw_file = project + ".hw"
    tree_file = project + ".tree"
    css_file = project + ".css"

    hw = parse_hw_file(hw_file)
    tree = parse_tree_file(tree_file)
    css = parse_css_file(css_file)

    run(hw, tree, css)
