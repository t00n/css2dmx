from .core import compute_animations

from .fixtures import *  # NOQA


def test_compute_animations(keyframe_parsed, animation_delay):
    assert(compute_animations(animation_delay, keyframe_parsed, 0) == {})
    assert(compute_animations(animation_delay, keyframe_parsed, 2.01) == {'color': [255, 0, 0, 254]})
    assert(compute_animations(animation_delay, keyframe_parsed, 4.51) == {'color': [255, 0, 0, 0]})
    assert(compute_animations(animation_delay, keyframe_parsed, 6.99) == {'color': [255, 0, 0, 254]})
