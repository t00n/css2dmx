from css import parse_color


def test_parse_color():
    assert parse_color('#000') == [0, 0, 0]
    assert parse_color('#B16') == [0xb0, 0x10, 0x60]
    assert parse_color('#000000') == [0, 0, 0]
    assert parse_color('#cafe00') == [0xca, 0xfe, 0]
    assert parse_color('rgb(0, 0, 0)') == [0, 0, 0]
    assert parse_color('rgb(10, 20,30)') == [10, 20, 30]
    assert parse_color('rgba(0, 0, 0, 1)') == [0, 0, 0, 255]
    assert parse_color('rgba(10, 20,30, 0.2)') == [10, 20, 30, 51]
