"""Token estimation.

A dependency-free heuristic (``max(words, ceil(chars/4))``) approximates LLM
token counts well enough to report savings. Install the ``tiktoken`` extra for an
exact count.
"""

from __future__ import annotations

import math


def estimate_tokens(text: str) -> int:
    """Cheap, dependency-free token estimate."""
    words = len(text.split())
    chars = math.ceil(len(text) / 4)
    return max(words, chars)


def count_tokens(text: str, *, exact: bool = False, model: str = "gpt-4o") -> int:
    """Exact count via tiktoken if available and requested, else the estimate."""
    if exact:
        try:  # pragma: no cover - requires optional dep
            import tiktoken
            try:
                enc = tiktoken.encoding_for_model(model)
            except Exception:
                enc = tiktoken.get_encoding("cl100k_base")
            return len(enc.encode(text))
        except Exception:
            pass
    return estimate_tokens(text)
