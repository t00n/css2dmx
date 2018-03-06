from lib.css import \
    parse_color, \
    parse_keyframe_frames, \
    Color

from .fixtures import *  # NOQA


def test_parse_color():
    assert parse_color('#000') == Color(0, 0, 0)
    assert parse_color('#B16') == Color(0xb0, 0x10, 0x60)
    assert parse_color('#000000') == Color(0, 0, 0)
    assert parse_color('#cafe00') == Color(0xca, 0xfe, 0)
    assert parse_color('rgb(0, 0, 0)') == Color(0, 0, 0)
    assert parse_color('rgb(10, 20,30)') == Color(10, 20, 30)
    assert parse_color('rgba(0, 0, 0, 1)') == Color(0, 0, 0, alpha=255)
    assert parse_color('rgba(10, 20,30, 0.2)') == Color(10, 20, 30, alpha=51)
    assert parse_color('rgbw(50, 60, 70, 80)') == Color(50, 60, 70, 80)
    assert parse_color('rgbwa(100, 110, 120, 130, 0.5)') == Color(100, 110, 120, 130, 127)
    assert parse_color('red-white') == Color(0, 0, 0, 0, 255, 'red-white')


def test_parse_keyframe_frames(keyframe_percentage, keyframe_fromto):
    parsed = parse_keyframe_frames(keyframe_percentage.content)
    assert(parsed[0].selector == 0)
    assert(parsed[0].properties[0].name == "color")
    assert(parsed[0].properties[0].value == Color(255, 0, 0, alpha=255))
    assert(parsed[1].selector == 50)
    assert(parsed[1].properties[0].name == "color")
    assert(parsed[1].properties[0].value == Color(255, 0, 0, alpha=0))
    assert(parsed[2].selector == 100)
    assert(parsed[2].properties[0].name == "color")
    assert(parsed[2].properties[0].value == Color(255, 0, 0, alpha=255))
    parsed = parse_keyframe_frames(keyframe_fromto.content)
    assert(parsed[0].selector == 0)
    assert(parsed[0].properties[0].name == "color")
    assert(parsed[0].properties[0].value == Color(255, 0, 0, alpha=255))
    assert(parsed[1].selector == 50)
    assert(parsed[1].properties[0].name == "color")
    assert(parsed[1].properties[0].value == Color(255, 0, 0, alpha=0))
    assert(parsed[2].selector == 100)
    assert(parsed[2].properties[0].name == "color")
    assert(parsed[2].properties[0].value == Color(255, 0, 0, alpha=255))


def test_parse_animation(animation_delay):
    anim = animation_delay
    assert(list(anim.keys()) == ['redintensity'])
    anim = anim['redintensity']
    assert(anim.duration == 5)
    assert(anim.function.name == "ease")
    assert(len(anim.function.params) == 0)
    assert(anim.delay == 2)
    assert(anim.iteration == "infinite")
    assert(anim.direction == "normal")
