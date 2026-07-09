from fra_translations.parser import parse_file


def run_quiz(path: str = "data/fra.txt") -> None:
    """Run an interactive quiz: show a random French phrase and ask for exact English translation.

    The user may type one of the accepted English translations exactly (trimmed). Type
    'q' or 'quit' to exit. Progress (correct/total) is shown on exit.
    """
    mapping = parse_file(path)
    if not mapping:
        print(f"No translations found in {path}")
        return

    import random

    total = 0
    correct = 0

    print("French -> English quiz. Type the exact English translation. Type 'q' to quit.")
    try:
        while True:
            fra = random.choice(list(mapping.keys()))
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
            if user in answers:
                correct += 1
                print('Correct!')
            else:
                print('Incorrect.')
                print('Expected one of:')
                for a in answers:
                    print('  -', a)
    except (KeyboardInterrupt, EOFError):
        print('\nExiting quiz.')

    print(f'You answered {correct}/{total} correctly.')


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "data/fra.txt"
    run_quiz(path)