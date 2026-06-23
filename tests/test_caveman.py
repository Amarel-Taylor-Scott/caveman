"""Offline tests — compression saves tokens AND preserves facts."""

from __future__ import annotations

from caveman import compress, estimate_tokens

SAMPLE = (
    "Could you please basically just summarize the report? "
    "Dr. Smith really wants the numbers, especially the $10,000 figure and the 42% increase. "
    "Do not skip the deadline on 2026-06-22. "
    "Check the endpoint at https://api.example.com/v1 and run `make deploy` to ship it."
)


def test_compression_saves_tokens():
    for level in (1, 2, 3):
        r = compress(SAMPLE, level=level)
        assert r.saved_tokens > 0, f"level {level} saved nothing"
        assert r.percent_saved > 0


def test_higher_level_compresses_at_least_as_much():
    t1 = compress(SAMPLE, level=1).compressed_tokens
    t2 = compress(SAMPLE, level=2).compressed_tokens
    t3 = compress(SAMPLE, level=3).compressed_tokens
    assert t1 >= t2 >= t3


def test_facts_preserved_at_all_levels():
    facts = ["$10,000", "42%", "2026-06-22", "Dr.", "Smith",
             "https://api.example.com/v1", "make deploy"]
    for level in (1, 2, 3):
        out = compress(SAMPLE, level=level).compressed
        for fact in facts:
            assert fact in out, f"lost {fact!r} at level {level}"


def test_negation_never_dropped():
    out = compress("This is not a problem and we should never ignore it.", level=3).compressed
    assert "not" in out.split()
    assert "never" in out.split()


def test_code_span_kept_verbatim():
    out = compress("Please run the `for x in the list: print(a)` snippet now.", level=3).compressed
    assert "`for x in the list: print(a)`" in out  # inside backticks untouched


def test_filler_actually_removed():
    out = compress("This is basically really just a very simple test.", level=1).compressed
    low = out.lower()
    assert "basically" not in low and "really" not in low and "simple" in low


def test_estimate_tokens():
    assert estimate_tokens("") == 0
    assert estimate_tokens("one two three") >= 3


def test_compress_clamps_level():
    assert compress("hello world", level=9).level == 3
    assert compress("hello world", level=0).level == 1
