"""fra_translations package

Provides a parser to build a French -> [English] mapping from a Tatoeba-style tab-separated file.
"""
from .parser import parse_file, parse_stream

__all__ = ["parse_file", "parse_stream"]
