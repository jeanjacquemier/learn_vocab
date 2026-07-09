from fra_translations.parser import parse_file


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_tsv_file>")
        sys.exit(1)

    path = sys.argv[1]
    mapping = parse_file(path)
    for fra, eng_list in mapping.items():
        print(f"{fra}: {', '.join(eng_list)}")