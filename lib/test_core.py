from .core import compute_animations

from .fixtures import *  # NOQA


def test_compute_animations_simple(keyframe_simple_parsed, animation_simple):
    assert(compute_animations(animation_simple, keyframe_simple_parsed, 0.01) == {'color': [255, 0, 0, 254]})
    assert(compute_animations(animation_simple, keyframe_simple_parsed, 2.50) == {'color': [255, 0, 0, 50]})
    assert(compute_animations(animation_simple, keyframe_simple_parsed, 4.99) == {'color': [255, 0, 0, 0]})


def test_compute_animations_delay(keyframe_parsed, animation_delay):
    assert(compute_animations(animation_delay, keyframe_parsed, 0) == {})
    assert(compute_animations(animation_delay, keyframe_parsed, 2.01) == {'color': [255, 0, 0, 254]})
    assert(compute_animations(animation_delay, keyframe_parsed, 4.51) == {'color': [255, 0, 0, 0]})
    assert(compute_animations(animation_delay, keyframe_parsed, 6.99) == {'color': [255, 0, 0, 254]})


def test_compute_animations_reverse(keyframe_simple_parsed, animation_reverse):
    assert(compute_animations(animation_reverse, keyframe_simple_parsed, 0.01) == {'color': [255, 0, 0, 0]})
    assert(compute_animations(animation_reverse, keyframe_simple_parsed, 2.51) == {'color': [255, 0, 0, 50]})
    assert(compute_animations(animation_reverse, keyframe_simple_parsed, 4.99) == {'color': [255, 0, 0, 254]})


def test_compute_animations_alternate(keyframe_simple_parsed, animation_alternate):
    assert(compute_animations(animation_alternate, keyframe_simple_parsed, 0.01) == {'color': [255, 0, 0, 254]})
    assert(compute_animations(animation_alternate, keyframe_simple_parsed, 2.51) == {'color': [255, 0, 0, 49]})
    assert(compute_animations(animation_alternate, keyframe_simple_parsed, 4.99) == {'color': [255, 0, 0, 0]})
    assert(compute_animations(animation_alternate, keyframe_simple_parsed, 7.51) == {'color': [255, 0, 0, 50]})
    assert(compute_animations(animation_alternate, keyframe_simple_parsed, 9.99) == {'color': [255, 0, 0, 254]})
    assert(compute_animations(animation_alternate, keyframe_simple_parsed, 10.01) == {'color': [255, 0, 0, 254]})
    assert(compute_animations(animation_alternate, keyframe_simple_parsed, 14.99) == {'color': [255, 0, 0, 0]})
