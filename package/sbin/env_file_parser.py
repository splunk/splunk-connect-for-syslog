"""Read SC4S env files as literal data, never shell code."""

import argparse
from pathlib import Path
import re
import sys

# Protect Bash internals and the entrypoint's loader/supervisor variables.
_RESERVED = {
    "BASHOPTS",
    "EUID",
    "PIPESTATUS",
    "PPID",
    "SHELLOPTS",
    "UID",
    "pid",
    "exit_code",
}


def read_env_file(path: Path, *, skip_invalid=False) -> dict[str, str | None]:
    """Read KEY=value entries, preserving everything after the first equals sign.

    Blank lines and comments are ignored; the last duplicate key wins.
    Quotes, dollar signs, backslashes and spaces in values are literal.
    In startup mode, bare names are tracked as None without being reassigned.
    """
    try:
        with open(path, encoding="utf-8-sig", newline="") as stream:
            contents = stream.read()
    except UnicodeError:
        raise ValueError(f"Invalid env_file {path}: expected UTF-8") from None

    assignments = {}
    for line_number, line in enumerate(contents.split("\n"), 1):
        line = line.removesuffix("\r").lstrip()
        if not line or line.startswith("#"):
            continue
        key, separator, value = line.partition("=")
        safe_name = (
            re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key)
            and not key.startswith(("_sc4s_env_", "BASH_"))
            and key not in _RESERVED
        )
        if not separator and safe_name and skip_invalid:
            assignments.setdefault(key, None)
        if not separator or not safe_name or "\0" in value:
            # Never include configuration values in errors.
            error = f"Invalid env_file {path}:{line_number}: expected a safe KEY=value entry"
            if skip_invalid:
                print(f"Warning: {error}; skipping line", file=sys.stderr)
                continue
            raise ValueError(error)
        assignments[key] = value
    return assignments


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--keys", action="store_true")
    parser.add_argument(
        "--skip-invalid",
        action="store_true",
        help="warn and skip unsupported startup entries",
    )
    args = parser.parse_args()
    try:
        assignments = read_env_file(args.path, skip_invalid=args.skip_invalid)
    except (OSError, ValueError) as error:
        print(
            (
                f"Warning: {error}; skipping env_file reload"
                if args.skip_invalid
                else error
            ),
            file=sys.stderr,
        )
        return 1
    if args.keys:
        sys.stdout.write("".join(f"{key}\n" for key in sorted(assignments)))
    else:
        sys.stdout.write(
            "".join(
                f"{key}={value}\n"
                for key, value in assignments.items()
                if value is not None
            )
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
