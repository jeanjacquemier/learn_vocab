import io
from fra_translations.parser import parse_stream


def test_parse_stream_basic():
    data = """Hello\tBonjour !\tsome meta
Hi\tSalut !\tmeta
Hello\tSalut !\tmeta
\nMalformedLine
\tNoEnglish\tmeta
"""
    stream = io.StringIO(data)
    mapping = parse_stream(stream)
    assert 'Bonjour !' in mapping
    assert mapping['Bonjour !'] == ['Hello']
    assert mapping['Salut !'] == ['Hi', 'Hello']


def test_parse_stream_empty():
    stream = io.StringIO('')
    mapping = parse_stream(stream)
    assert mapping == {}
