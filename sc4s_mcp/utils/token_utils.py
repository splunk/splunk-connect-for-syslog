"""Shared helper for loading bearer tokens from env var or secret file."""

import os


def load_token(token_env: str, token_file_env: str) -> str:
    """Return a bearer token resolved from env vars.

    Reads ``token_file_env`` first; if set, returns the file contents (stripped).
    Otherwise falls back to ``token_env``. Returns an empty string when neither is set.
    Raises ``RuntimeError`` if the file path is set but cannot be read.
    """
    token_file = (os.environ.get(token_file_env) or "").strip()
    if token_file:
        try:
            with open(token_file) as f:
                return f.read().strip()
        except OSError as exc:
            raise RuntimeError(
                f"Cannot read {token_file_env}={token_file!r}: {exc}"
            ) from exc
    return os.environ.get(token_env, "")
