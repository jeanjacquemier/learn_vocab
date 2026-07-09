Learn vocubulary 
=======

Small Python package to parse `data/fra.txt` (Tatoeba-like tab-separated file) and build a French -> [English] mapping.

Install (recommended: use a venv):

# create venv
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]

Run tests:

pytest -q

Usage from Python:

from fra_translations import parse_file
mapping = parse_file('data/fra.txt')
print(mapping.get('Bonjour !'))

Or use the CLI (not yet added) to dump JSON.
