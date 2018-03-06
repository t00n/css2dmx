import json
from glob import glob
from logging import getLogger

from jsonschema import validate

logger = getLogger(__name__)

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

channel_schema = {
    "type": "object",
    "properties": {
        "chan": address_schema,
        "range": range_schema
    },
    "required": [
        "chan"
    ],
    "additionalProperties": False
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
        "white": channel_schema,
        "alpha": channel_schema,
        "name": enum_schema([])
    },
    "additionalProperties": False
}

# STROBE
strobe_schema = {
    "type": "object",
    "properties": {
        "speed": channel_schema
    },
    "additionalProperties": False
}

# PULSE
pulse_direction_schema = {
    "type": "object",
    "properties": {
        "chan": address_schema,
        "enum": enum_schema(["normal", "reverse", "alternate"], required=True)
    },
    "required": [
        "chan",
        "enum"
    ],
    "additionalProperties": False
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
    ],
    "additionalProperties": False
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
    ],
    "additionalProperties": False
}

auto_schema = {
    "type": "object",
    "properties": {
        "name": auto_value_schema,
        "speed": channel_schema
    },
    "required": [
        "name"
    ],
    "additionalProperties": False
}

# ROTATION
rotation_schema = {
    "type": "object",
    "properties": {
        "position": channel_schema,
        "speed": channel_schema
    },
    "minProperties": 1,
    "additionalProperties": False
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
                "auto": auto_schema,
                "rotation": rotation_schema
            }
        }
    },
    "additionalProperties": False
}


def load_devices():
    devices = {}
    for file in glob("devices/*"):
        with open(file) as f:
            data = json.load(f)
        validate(data, schema)
        name = data['name']
        if name in devices:
            logger.warn("overwriting device {}".format(name))
        devices[name] = data['mapping']
    return devices
