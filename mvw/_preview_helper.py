import sys
import re
import pathlib


def main():
    if len(sys.argv) < 3:
        return
    cache_dir = pathlib.Path(sys.argv[1])
    selection = sys.argv[2].strip()

    # Mode 1: fzf list mode - selection is "[tt...] Movie Title"
    m = re.match(r"\[(tt\d+)\]", selection)
    imdbid = m.group(1) if m else None

    # Mode 2: menu mode - selection is a raw imdbid
    if not imdbid and re.match(r"^tt\d+$", selection):
        imdbid = selection

    if not imdbid:
        return

    cache_file = cache_dir / f"{imdbid}.txt"
    if cache_file.exists():
        sys.stdout.buffer.write(cache_file.read_bytes())


if __name__ == "__main__":
    main()
