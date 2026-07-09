from fra_translations.parser import parse_file

import argparse
import json
import os
import random
from typing import Dict


def load_scores(path: str) -> Dict[str, int]:
    if not os.path.exists(path):
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            return json.load(fh)
    except Exception:
        return {}


def save_scores(path: str, scores: Dict[str, int]) -> None:
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(scores, fh, ensure_ascii=False, indent=2)


def load_pool(path: str) -> list:
    if not os.path.exists(path):
        return []
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            return json.load(fh)
    except Exception:
        return []


def save_pool(path: str, pool: list) -> None:
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(pool, fh, ensure_ascii=False, indent=2)


def run_quiz(path: str = "data/fra.txt", scores_path: str = "data/scores.json", ignore_case: bool = False, allow_multiword: bool = False, pool_path: str = "data/pool.json", pool_size: int = 10) -> None:
    """Run an interactive quiz: show a random French phrase and ask for exact English translation.

    Each French entry has a score persisted to `scores_path`.
    - Correct answer: score += 1
    - Incorrect answer: score = 0
    """
    mapping = parse_file(path)
    if not mapping:
        print(f"No translations found in {path}")
        return

    scores = load_scores(scores_path)
    # Ensure all phrases have a score
    for fra in mapping.keys():
        scores.setdefault(fra, 0)

    total = 0
    correct = 0

    print("French -> English quiz. Type the exact English translation. Type 'q' to quit.")
    if not allow_multiword:
        # keep only entries that are a single token when split on whitespace
        single_keys = [k for k in mapping.keys() if len(k.split()) == 1]
        if not single_keys:
            print("No single-word entries found; falling back to full dictionary.")
            keys = list(mapping.keys())
        else:
            keys = single_keys
    else:
        keys = list(mapping.keys())

    # Load or initialize pool: persistent list of phrases to propose
    pool = load_pool(pool_path)
    # Validate pool: keep only keys that still exist and have score < 5 or keep anyway
    pool = [k for k in pool if k in keys]
    # fill pool up to pool_size with lowest-scored candidates not already in pool
    candidates = [k for k in keys if k not in pool]
    # load scores to pick low-score candidates
    scores = load_scores(scores_path)
    # ensure scores keys exist
    for fra in keys:
        scores.setdefault(fra, 0)
    # sort candidates by score ascending
    candidates.sort(key=lambda x: int(scores.get(x, 0)))
    while len(pool) < min(pool_size, len(keys)) and candidates:
        pool.append(candidates.pop(0))
    # if pool ends up empty, fallback to keys
    if not pool:
        pool = keys
    # save initial pool
    save_pool(pool_path, pool)
    try:
        while True:
            fra = random.choice(pool)
            answers = mapping.get(fra, [])
            print('\nTranslate:')
            print(fra)
            user = input('Your translation (or q to quit): ').strip()
            if not user:
                print('Please type a translation or q to quit.')
                continue
            if user.lower() in ("q", "quit"):
                break
            total += 1
            match_found = False
            if ignore_case:
                u = user.casefold()
                answers_cf = [a.casefold() for a in answers]
                if u in answers_cf:
                    match_found = True
            else:
                if user in answers:
                    match_found = True

            if match_found:
                correct += 1
                scores[fra] = int(scores.get(fra, 0)) + 1
                save_scores(scores_path, scores)
                print('Correct!')
                print(f"Score for '{fra}': {scores[fra]}")
                # if score reached threshold, remove from pool and add replacement
                if scores[fra] >= 5:
                    try:
                        pool.remove(fra)
                        # find replacement among candidates not in pool and score < 5
                        remaining = [k for k in keys if k not in pool and k != fra]
                        remaining.sort(key=lambda x: int(scores.get(x, 0)))
                        if remaining:
                            pool.append(remaining[0])
                            print(f"'{fra}' reached score >=5 and was removed from the pool. Added '{remaining[0]}' to the pool.")
                        else:
                            print(f"'{fra}' reached score >=5 and was removed from the pool. No replacement available.")
                    except ValueError:
                        pass
                    save_pool(pool_path, pool)
            else:
                scores[fra] = 0
                save_scores(scores_path, scores)
                print('Incorrect.')
                print('Expected one of:')
                for a in answers:
                    print('  -', a)
                print(f"Score for '{fra}' has been reset to 0")
    except (KeyboardInterrupt, EOFError):
        print('\nExiting quiz.')

    print(f'You answered {correct}/{total} correctly.')


def _main(argv=None):
    p = argparse.ArgumentParser(description='French->English quiz')
    p.add_argument('tsv', nargs='?', default='data/fra.txt', help='path to the TSV file')
    p.add_argument('--scores', default='data/scores.json', help='path to scores JSON file')
    p.add_argument('--ignore-case', action='store_true', help='match answers case-insensitively')
    p.add_argument('--allow-multiword', action='store_true', help='allow multi-word French entries (default: only single-word entries)')
    p.add_argument('--pool', default='data/pool.json', help='path to persistent pool file')
    p.add_argument('--pool-size', default=10, type=int, help='number of words kept in the pool')
    args = p.parse_args(argv)
    run_quiz(args.tsv, args.scores, args.ignore_case, args.allow_multiword, pool_size=args.pool_size, pool_path=args.pool)


if __name__ == "__main__":
    _main()