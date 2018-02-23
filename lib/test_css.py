from css import parse_color, \
    parse_keyframe_frames

from fixtures import *  # NOQA


def test_parse_color():
    assert parse_color('#000') == [0, 0, 0]
    assert parse_color('#B16') == [0xb0, 0x10, 0x60]
    assert parse_color('#000000') == [0, 0, 0]
    assert parse_color('#cafe00') == [0xca, 0xfe, 0]
    assert parse_color('rgb(0, 0, 0)') == [0, 0, 0]
    assert parse_color('rgb(10, 20,30)') == [10, 20, 30]
    assert parse_color('rgba(0, 0, 0, 1)') == [0, 0, 0, 255]
    assert parse_color('rgba(10, 20,30, 0.2)') == [10, 20, 30, 51]


def test_parse_keyframe_frames(keyframe_percentage, keyframe_fromto):
    parsed = parse_keyframe_frames(keyframe_percentage.content)
    assert(parsed[0].selector == 0)
    assert(parsed[0].properties[0].name == "color")
    assert(parsed[0].properties[0].value == [255, 0, 0, 255])
    assert(parsed[1].selector == 50)
    assert(parsed[1].properties[0].name == "color")
    assert(parsed[1].properties[0].value == [255, 0, 0, 0])
    assert(parsed[2].selector == 100)
    assert(parsed[2].properties[0].name == "color")
    assert(parsed[2].properties[0].value == [255, 0, 0, 255])
    parsed = parse_keyframe_frames(keyframe_fromto.content)
    assert(parsed[0].selector == 0)
    assert(parsed[0].properties[0].name == "color")
    assert(parsed[0].properties[0].value == [255, 0, 0, 255])
    assert(parsed[1].selector == 50)
    assert(parsed[1].properties[0].name == "color")
    assert(parsed[1].properties[0].value == [255, 0, 0, 0])
    assert(parsed[2].selector == 100)
    assert(parsed[2].properties[0].name == "color")
    assert(parsed[2].properties[0].value == [255, 0, 0, 255])


def test_parse_animation(animation_delay):
    anim = animation_delay
    assert(list(anim.keys()) == ['redintensity'])
    anim = anim['redintensity']
    assert(anim.duration == 5)
    assert(anim.function.name == "ease")
    assert(len(anim.function.params) == 0)
    assert(anim.delay == 2)
    assert(anim.iteration == "infinite")
    assert(anim.direction == "alternate")
