from lib.core import compute_animations
from lib.css import Color

from .fixtures import *  # NOQA


def test_compute_animations_simple(keyframe_simple_parsed, animation_simple):
    assert(compute_animations(animation_simple, keyframe_simple_parsed, 0.01) == {'color': Color(255, 0, 0, alpha=254)})
    assert(compute_animations(animation_simple, keyframe_simple_parsed, 2.50) == {'color': Color(255, 0, 0, alpha=50)})
    assert(compute_animations(animation_simple, keyframe_simple_parsed, 4.99) == {'color': Color(255, 0, 0, alpha=0)})


def test_compute_animations_delay(keyframe_parsed, animation_delay):
    assert(compute_animations(animation_delay, keyframe_parsed, 0) == {})
    assert(compute_animations(animation_delay, keyframe_parsed, 2.01) == {'color': Color(255, 0, 0, alpha=254)})
    assert(compute_animations(animation_delay, keyframe_parsed, 4.51) == {'color': Color(255, 0, 0, alpha=0)})
    assert(compute_animations(animation_delay, keyframe_parsed, 6.99) == {'color': Color(255, 0, 0, alpha=254)})


def test_compute_animations_reverse(keyframe_simple_parsed, animation_reverse):
    assert(compute_animations(animation_reverse, keyframe_simple_parsed, 0.01) == {'color': Color(255, 0, 0, alpha=0)})
    assert(compute_animations(animation_reverse, keyframe_simple_parsed, 2.51) == {'color': Color(255, 0, 0, alpha=50)})
    assert(compute_animations(animation_reverse, keyframe_simple_parsed, 4.99) == {'color': Color(255, 0, 0, alpha=254)})


def test_compute_animations_alternate(keyframe_simple_parsed, animation_alternate):
    assert(compute_animations(animation_alternate, keyframe_simple_parsed, 0.01) == {'color': Color(255, 0, 0, alpha=254)})
    assert(compute_animations(animation_alternate, keyframe_simple_parsed, 2.51) == {'color': Color(255, 0, 0, alpha=49)})
    assert(compute_animations(animation_alternate, keyframe_simple_parsed, 4.99) == {'color': Color(255, 0, 0, alpha=0)})
    assert(compute_animations(animation_alternate, keyframe_simple_parsed, 7.51) == {'color': Color(255, 0, 0, alpha=50)})
    assert(compute_animations(animation_alternate, keyframe_simple_parsed, 9.99) == {'color': Color(255, 0, 0, alpha=254)})
    assert(compute_animations(animation_alternate, keyframe_simple_parsed, 10.01) == {'color': Color(255, 0, 0, alpha=254)})
    assert(compute_animations(animation_alternate, keyframe_simple_parsed, 14.99) == {'color': Color(255, 0, 0, alpha=0)})


def test_compute_animations_alternate_reverse(keyframe_simple_parsed, animation_alternate_reverse):
    assert(compute_animations(animation_alternate_reverse, keyframe_simple_parsed, 0.01) == {'color': Color(255, 0, 0, alpha=0)})
    assert(compute_animations(animation_alternate_reverse, keyframe_simple_parsed, 2.51) == {'color': Color(255, 0, 0, alpha=50)})
    assert(compute_animations(animation_alternate_reverse, keyframe_simple_parsed, 4.99) == {'color': Color(255, 0, 0, alpha=254)})
    assert(compute_animations(animation_alternate_reverse, keyframe_simple_parsed, 7.51) == {'color': Color(255, 0, 0, alpha=49)})
    assert(compute_animations(animation_alternate_reverse, keyframe_simple_parsed, 9.99) == {'color': Color(255, 0, 0, alpha=0)})
    assert(compute_animations(animation_alternate_reverse, keyframe_simple_parsed, 10.01) == {'color': Color(255, 0, 0, alpha=0)})
    assert(compute_animations(animation_alternate_reverse, keyframe_simple_parsed, 14.99) == {'color': Color(255, 0, 0, alpha=254)})
