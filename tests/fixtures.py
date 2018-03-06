import pytest
import tinycss2

from lib.css import parse_animation, parse_keyframes


@pytest.fixture
def keyframe_percentage():
    return tinycss2.parse_stylesheet("""
        @keyframes redintensity {
            0%, 100% {
                color: rgba(255, 0, 0, 1);
            }
            50% {
                color: rgba(255, 0, 0, 0);
            }
        }
    """)[1]


@pytest.fixture
def keyframe_fromto():
    return tinycss2.parse_stylesheet("""
        @keyframes redintensity {
            from, to {
                color: rgba(255, 0, 0, 1);
            }
            50% {
                color: rgba(255, 0, 0, 0);
            }
        }
    """)[1]


@pytest.fixture
def keyframe_simple():
    return tinycss2.parse_stylesheet("""
        @keyframes redintensity {
            from {
                color: rgba(255, 0, 0, 1);
            }
            to {
                color: rgba(255, 0, 0, 0);
            }
        }
    """)[1]


@pytest.fixture
def keyframe_simple_parsed(keyframe_simple):
    return parse_keyframes([keyframe_simple])


@pytest.fixture
def keyframe_parsed(keyframe_percentage):
    return parse_keyframes([keyframe_percentage])


@pytest.fixture
def animation_simple():
    return parse_animation("redintensity 5s ease 0s infinite normal")


@pytest.fixture
def animation_delay():
    return parse_animation("redintensity 5s ease 2s infinite normal")


@pytest.fixture
def animation_reverse():
    return parse_animation("redintensity 5s ease 0s infinite reverse")


@pytest.fixture
def animation_alternate():
    return parse_animation("redintensity 5s ease 0s infinite alternate")


@pytest.fixture
def animation_alternate_reverse():
    return parse_animation("redintensity 5s ease 0s infinite alternate-reverse")
