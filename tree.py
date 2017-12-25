import json


def set_node_style(node, style):
    if 'style' not in node:
        node['style'] = {}
    for prop in style:
        node['style'][prop.name] = prop.value


def select_nodes(path, tree):
    for id, node in walk_tree(tree):
        if path[0] == "#" and path[1:] == id:
            yield id, node
        elif path[0] == "." and path[1:] in node.get('class', "").split(" "):
            yield id, node


def walk_node(id, node):
    children = node.get('children', {})
    yield id, node
    for n, child in children.items():
        yield from walk_node(n, child)


def walk_tree(tree):
    for id, child in tree.items():
        yield from walk_node(id, child)


def parse_node(id, node):
    if 'class' in node and not isinstance(node['class'], str):
        raise Exception("Expected 'class' in '{}' to be a str, got '{}'".format(id, node['class']))
    if 'children' in node and not isinstance(node['children'], dict):
        raise Exception("Expected 'children' in '{}' to be a dict, got '{}'".format(id, node['children']))
    for id, child in node.get('children', {}).items():
        parse_node(id, child)


def parse_tree(content):
    if not isinstance(content, dict):
        raise Exception("Expected root to be a dict, got {}".format(content))
    for id, child in content.items():
        parse_node(id, child)
    return content


def parse_tree_file(fileid):
    with open("yolo.tree") as f:
        content = json.load(f)
    return parse_tree(content)


if __name__ == '__main__':
    res = parse_tree_file("yolo.tree")
    print(res)
    for id, node in walk_tree(res):
        print(id, node)
