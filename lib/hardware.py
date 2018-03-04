from collections import defaultdict
import json
from jsonschema import validate

# BASIC
address_schema = {
    "type": "integer",
    "minimum": 1,
    "maximum": 512
}

value_schema = {
    "type": "integer",
    "minimum": 0,
    "maximum": 255
}

range_schema = {
    "type": "array",
    "items": [
        value_schema,
        value_schema
    ]
}

cond_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "chan": address_schema,
            "range": range_schema
        },
        "required": [
            "chan",
            "range"
        ]
    }
}

channel_schema = {
    "type": "object",
    "properties": {
        "chan": address_schema,
        "range": range_schema,
        "cond": cond_schema
    },
    "required": [
        "chan"
    ]
}


def enum_schema(values, *, required=False):
    res = {
        "type": "object",
        "properties": {v: range_schema for v in values}
    }
    if required:
        res['required'] = values
    return res

# COLOR
color_schema = {
    "type": "object",
    "properties": {
        "red": channel_schema,
        "green": channel_schema,
        "blue": channel_schema,
        "alpha": channel_schema
    },
    "required": [
        "red",
        "green",
        "blue"
    ]
}

# STROBE
strobe_schema = {
    "type": "object",
    "properties": {
        "speed": channel_schema
    }
}

# PULSE
pulse_direction_schema = {
    "type": "object",
    "properties": {
        "chan": address_schema,
        "enum": enum_schema(["none", "normal", "reverse", "alternate"], required=True)
    },
    "required": [
        "chan",
        "enum"
    ]
}

pulse_schema = {
    "type": "object",
    "properties": {
        "speed": channel_schema,
        "direction": pulse_direction_schema
    },
    "required": [
        "speed",
        "direction"
    ]
}

# AUTO
auto_value_schema = {
    "type": "object",
    "properties": {
        "chan": address_schema,
        "enum": enum_schema(["fade-transition", "snap-3", "snap-7", "sound"])
    },
    "required": [
        "chan",
        "enum"
    ]
}

auto_schema = {
    "type": "object",
    "properties": {
        "value": auto_value_schema
    },
    "required": [
        "value"
    ]
}

# ROOT
schema = {
    "$schema": "http://json-schema.org/schema#",
    "type": "object",
    "properties": {
        "name": {
            "type": "string"
        },
        "mapping": {
            "type": "object",
            "properties": {
                "color": color_schema,
                "strobe": strobe_schema,
                "pulse": pulse_schema,
                "auto": auto_schema
            }
        }
    }
}


def load_devices():
    from glob import glob
    devices = {}
    for file in glob("devices/*"):
        with open(file) as f:
            data = json.load(f)
        validate(data, schema)
        name = data['name']
        if name in devices:
            print("WARNING: overwriting device {}".format(name))
        devices[name] = data['mapping']
    return devices
