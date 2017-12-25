import json


class Node:
    def __init__(self, id, children=[], klass=""):
        self.id = id
        self.children = children
        self.klass = klass.split(" ")
        self.style = {}

    def add_style(self, name, value):
        self.style[name] = value

    def walk(self):
        yield self
        for child in self:
            yield from child.walk()

    def select(self, path):
        for node in self.walk():
            if path[0] == "#" and path[1:] == node.id:
                yield node
            elif path[0] == "." and path[1:] in node.klass:
                yield node

    def __iter__(self):
        yield from self.children

    def __str__(self):
        return "<Node id={} children={} klass={} style={}>".format(self.id, list(self.children.keys()), self.klass, self.style)


def parse_node(id, node):
    if not isinstance(node, dict):
        raise Exception("Expected '{}' to be a dict, got {}".format(id, node))
    if 'class' in node and not isinstance(node['class'], str):
        raise Exception("Expected 'class' in '{}' to be a str, got '{}'".format(id, node['class']))
    if 'children' in node and not isinstance(node['children'], dict):
        raise Exception("Expected 'children' in '{}' to be a dict, got '{}'".format(id, node['children']))
    children = [parse_node(id, child) for id, child in node.get('children', {}).items()]
    return Node(id, klass=node.get('class', ''), children=children)


def parse_tree(content):
    return parse_node("$root$", content)


def parse_tree_file(fileid):
    with open("yolo.tree") as f:
        content = json.load(f)
    return parse_tree(content)


if __name__ == '__main__':
    res = parse_tree_file("yolo.tree")
    for node in res.walk():
        print(node)
