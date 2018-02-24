from core import compute_animations

from fixtures import *  # NOQA


def test_compute_animations(keyframe_parsed, animation_delay):
    assert(compute_animations(animation_delay, keyframe_parsed, 3) == {'color': [255, 0, 0, 80]})
    assert(compute_animations(animation_delay, keyframe_parsed, 0) == {})
    assert(compute_animations(animation_delay, keyframe_parsed, 5) == {'color': [255, 0, 0, 75]})
