from xml.etree import ElementTree as ET


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


def parse_node(node):
    children = [parse_node(child) for child in node]
    return Node(node.tag, klass=node.attrib.get('class', ''), children=children)


def parse_tree_file(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    return parse_node(root)


if __name__ == '__main__':
    res = parse_tree_file("yolo.tree")
    for node in res.walk():
        print(node)
