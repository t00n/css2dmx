import json


class Node:
    def __init__(self, id, children=[], klass=""):
        self.id = id
        self.children = children
        self.klass = klass.split(" ")
        self.style = {}

    def add_style(self, name, value):
        self.style[name] = value
        for c in self.children:
            c.add_style(name, value)

    def walk(self):
        yield self
        for child in self:
            yield from child.walk()

    def select(self, selector):
        for node in self.walk():
            if selector.type == 'id' and selector.value == node.id:
                yield node
            elif selector.type == 'class' and selector.value in node.klass:
                yield node

    def __iter__(self):
        yield from self.children

    def __str__(self):
        return "<Node id={} children={} klass={} style={}>".format(self.id, [c.id for c in self.children], self.klass, self.style)

    def print(self, level=0):
        if level != 0:
            print(' ' * level + '└', end="")
        print(str(self))
        for child in self.children:
            child.print(level + 1)


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


def parse_tree_file(filename):
    with open(filename) as f:
        content = json.load(f)
    return parse_tree(content)


if __name__ == '__main__':
    res = parse_tree_file("yolo.tree")
    for node in res.walk():
        print(node)
