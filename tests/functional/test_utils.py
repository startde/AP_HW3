import pytest
from src.utils import encode, decode

@pytest.mark.parametrize("num, expected", [
    (0, "0"),  # Ожидаемый результат для 0
])
def test_encode_zero(num, expected):
    assert encode(num) == expected

@pytest.mark.parametrize("string, expected", [
    ("0", 0),  # Ожидаемый результат для "0"
])
def test_decode_zero(string, expected):
    assert decode(string) == expected

@pytest.mark.parametrize("string, expected", [
    ("1", 1),  # Пример для небольшой строки
    ("a", 10),  # Проверка букв алфавита
    ("Z", 61),  # Последний символ алфавита
    ("10", 62),  # Переход к двузначным значениям
])
def test_decode_small_strings(string, expected):
    assert decode(string) == expected

@pytest.mark.parametrize("string", [
    "-",  # Недопустимый символ
])
def test_decode_invalid_characters(string):
    with pytest.raises(ValueError):
        decode(string)