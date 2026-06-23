"""Deterministic prompt/context compression — "talk like a caveman".

The idea (popularized by the *caveman* prompt-compression trend): LLMs don't need
grammatical filler to understand you. Stripping predictable, low-information words
keeps the meaning while cutting tokens.

This is a clean-room reimplementation with a hard safety rule: **never drop
information-bearing tokens** — numbers, code spans, URLs/emails, capitalized words
(proper nouns / acronyms), and *negations* (not/no/never/without/…). Compression
is lossy on grammar, never on facts.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass

from .tokens import count_tokens

# --- word sets per level (cumulative) ---
_FILLER = {
    "basically", "actually", "really", "very", "just", "simply", "literally",
    "honestly", "essentially", "totally", "quite", "rather", "somewhat",
    "obviously", "clearly", "truly", "absolutely", "particularly",
}
_POLITENESS = {"please", "thanks", "thank", "kindly", "hello", "hi", "regards"}
_ARTICLES = {"a", "an", "the"}
_SOFT_ADVERBS = {"currently", "generally", "typically", "usually", "often",
                 "perhaps", "maybe", "probably", "certainly", "definitely"}
_AUX = {"is", "are", "am", "was", "were", "be", "been", "being", "do", "does",
        "did", "has", "have", "had", "will", "would", "shall", "should"}
_PREP_LOW = {"of", "to", "in", "on", "at", "for", "with", "as", "by", "that"}

# NEVER dropped (override every level).
_NEGATIONS = {
    "not", "no", "never", "none", "nor", "neither", "without", "cannot",
    "dont", "doesnt", "didnt", "isnt", "arent", "wasnt", "werent", "cant",
    "wont", "shouldnt", "wouldnt", "couldnt", "nothing", "nobody",
}

_LEVELS = {
    1: _FILLER | _POLITENESS,
    2: _FILLER | _POLITENESS | _ARTICLES | _SOFT_ADVERBS,
    3: _FILLER | _POLITENESS | _ARTICLES | _SOFT_ADVERBS | _AUX | _PREP_LOW,
}

_TECHNICAL = re.compile(r"[\d/@_]|://|\\")
_TERMINAL = re.compile(r"[.!?;:,]+$")
_CODE_SPAN = re.compile(r"(`[^`]*`)")


@dataclass
class Compression:
    original: str
    compressed: str
    level: int
    original_tokens: int
    compressed_tokens: int

    @property
    def saved_tokens(self) -> int:
        return self.original_tokens - self.compressed_tokens

    @property
    def percent_saved(self) -> float:
        if self.original_tokens == 0:
            return 0.0
        return round(100 * self.saved_tokens / self.original_tokens, 1)


def _core(token: str) -> str:
    return "".join(c for c in token.lower() if c.isalnum())


def _is_protected(token: str, core: str) -> bool:
    if not core:
        return True                       # punctuation-only
    if _TECHNICAL.search(token):
        return True                       # numbers, paths, URLs, identifiers
    if core in _NEGATIONS:
        return True                       # never lose negation
    if token[0].isupper():
        return True                       # proper noun / acronym / sentence start
    return False


def _compress_words(text: str, stop: set[str]) -> str:
    out: list[str] = []
    for token in text.split():
        core = _core(token)
        if _is_protected(token, core):
            out.append(token)
            continue
        if core in stop:
            m = _TERMINAL.search(token)
            if m and out:                 # salvage sentence-ending punctuation
                out[-1] = out[-1] + m.group(0)
            continue
        out.append(token)
    return " ".join(out)


def compress(text: str, level: int = 2, *, exact_tokens: bool = False) -> Compression:
    level = max(1, min(3, int(level)))
    stop = _LEVELS[level]
    parts = _CODE_SPAN.split(text)
    rebuilt = []
    for i, part in enumerate(parts):
        if i % 2 == 1:                    # a `code span` — keep verbatim
            rebuilt.append(part)
        else:
            rebuilt.append(_compress_words(part, stop))
    compressed = re.sub(r"\s+", " ", " ".join(p for p in rebuilt if p)).strip()
    return Compression(
        original=text,
        compressed=compressed,
        level=level,
        original_tokens=count_tokens(text, exact=exact_tokens),
        compressed_tokens=count_tokens(compressed, exact=exact_tokens),
    )
