import pytest

from package.shared.pylib.parser_cef import _parse_cef_ext

testdata = [
    # Basic key/value pairs.
    ("key1=val1 key2=val2", [("key1", "val1"), ("key2", "val2")]),
    (
        "key1=val1 with spaces key2=val2",
        [("key1", "val1 with spaces"), ("key2", "val2")],
    ),
    # Regression: a value containing '=' (e.g. a URL query string) must not
    # be split on the inner '='.
    (
        "url=http://example.com?a=1&b=2 status=200",
        [("url", "http://example.com?a=1&b=2"), ("status", "200")],
    ),
    # Escaped '\=' is treated as an in-value equals, not a key boundary.
    (
        "key1=part1\\=part2 key2=val2",
        [("key1", "part1\\=part2"), ("key2", "val2")],
    ),
    # Empty values are dropped.
    ("a= b=2", [("b", "2")]),
    # No '=' at all: no pairs, and no quadratic blow-up / crash.
    ("just some text with no equals signs here", []),
    # Empty input.
    ("", []),
    # Label fields keep their own key/value pairs intact.
    ("cs1Label=Foo cs1=bar", [("cs1Label", "Foo"), ("cs1", "bar")]),
]

@pytest.mark.parametrize("data, expected", testdata)
def test_parse_cef_ext(data, expected):
    assert _parse_cef_ext(data) == expected
