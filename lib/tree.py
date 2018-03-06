from xml.etree import ElementTree as ET


class Node:
    def __init__(self, tag, *, offset=0, id='', children=[], klass=""):
        self.tag = tag
        self.offset = offset
        self.id = id
        self.children = children
        self.klass = klass.split(" ")
        self.style = {}

    def add_style(self, prop, value):
        self.style[prop] = value
        for c in self.children:
            c.add_style(prop, value)

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
            elif selector.type == 'tag' and selector.value == node.tag:
                yield node

    def __iter__(self):
        yield from self.children

    def __str__(self):
        return "<Node tag={} id={} children={} klass={} style={}>".format(self.tag,
                                                                          self.id,
                                                                          [c.id for c in self.children],
                                                                          self.klass,
                                                                          self.style)

    def print(self, level=0):
        if level != 0:
            print(' ' * level + '└', end="")
        print(str(self))
        for child in self.children:
            child.print(level + 1)


def parse_node(node):
    children = [parse_node(child) for child in node]
    return Node(node.tag,
                offset=int(node.attrib.get('offset', 0)),
                id=node.attrib.get('id', ''),
                klass=node.attrib.get('class', ''),
                children=children)


def parse_tree_file(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    return parse_node(root)
