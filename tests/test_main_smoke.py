from fra_translations.main import run_quiz
from fra_translations import parse_file


def test_run_quiz_function_exists():
    # smoke: ensure run_quiz is callable and parse_file loads the provided data file
    mapping = parse_file('data/fra.txt')
    assert isinstance(mapping, dict)
    # do not actually call run_quiz (interactive)
    assert callable(run_quiz)
