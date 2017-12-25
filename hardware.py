from collections import defaultdict
import json


# checks that the address is an integer between 0 and 255
def parse_address(addr):
    try:
        addr = int(addr)
        if addr < 0 or addr > 255:
            raise Exception()
        return addr
    except:
        raise Exception("Expected an hexadecimal address between 0x00 and 0xff, got {}".format(addr))


# a color is a list of 3 addresses
def parse_color(data):
    if len(data) == 3:
        return [parse_address(x) for x in data]
    else:
        raise Exception("Expected (red, green, blue) for color, got {}".format(data))


# a rotation is a single address
def parse_rotation(data):
    return [parse_address(data)]


def parse_property(name, data):
    if name == "color":
        return parse_color(data)
    elif name == "rotation":
        return parse_rotation(data)
    else:
        raise Exception("Undefined property: {}".format(name))


def parse_device(name, desc):
    if not isinstance(desc, dict):
        raise Exception("Expected device to be a dict, got {}".format(desc))
    return [x for name, props in desc.items() for x in parse_property(name, props)]


def parse_hw(root):
    if not isinstance(root, dict):
        raise Exception("Expected a dict on root-level, got {}".format(root))
    addresses = defaultdict(set)
    for name, desc in root.items():
        device_addresses = parse_device(name, desc)
        for other_name, other_addresses in addresses.items():
            for addr in device_addresses:
                if addr in other_addresses:
                    print("WARNING: address {} in '{}' conflicts with '{}'".format(addr, name, other_name))
        addresses[name].update(device_addresses)
    return root


def parse_hw_file(filename):
    with open(filename) as f:
        obj = json.load(f)
    return parse_hw(obj)


if __name__ == '__main__':
    res = parse_hw_file("yolo.hw")
    print(res)
