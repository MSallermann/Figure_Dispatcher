import os as _os

repo_path = _os.path.abspath(_os.path.dirname(__file__))
data_path = _os.path.join(repo_path, "Data")
spirit_path = "/home/moritz/Coding/spirit"

_choices = [
    v for v in globals() if v[:1] != "_" and v[-1:] != "_"
]  # exclude all vars with underscores


def _main(string):
    return globals()[string]


if __name__ == "__main__":
    # prints the requested paths (Use in shell script e.g as `SPIRIT_PATH=$( python3 __paths__.py spirit_path)`)
    import argparse as _argparse

    _parser = _argparse.ArgumentParser()

    _parser.add_argument("which", choices=_choices)
    _args = _parser.parse_args()

    print(_main(_args.which))
