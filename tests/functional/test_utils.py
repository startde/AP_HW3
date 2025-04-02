import pytest
from src.utils import encode, decode

@pytest.mark.parametrize("num, expected", [
    (0, "0"),  
])
def test_encode_zero(num, expected):
    assert encode(num) == expected

@pytest.mark.parametrize("string, expected", [
    ("0", 0),  
])
def test_decode_zero(string, expected):
    assert decode(string) == expected

@pytest.mark.parametrize("string, expected", [
    ("1", 1),
    ("a", 10), 
    ("Z", 61), 
    ("10", 62),
])
def test_decode_small_strings(string, expected):
    assert decode(string) == expected

@pytest.mark.parametrize("string", [
    "-",
])
def test_decode_invalid_characters(string):
    with pytest.raises(ValueError):
        decode(string)