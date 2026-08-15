"""UNG adapter registry for caveman (see nodepacker's ADAPTER_SPEC.md).

Pure JSON-in/JSON-out wrappers over :mod:`caveman.compress` and
:mod:`caveman.tokens`. Only the dependency-free estimator path is exposed;
the optional tiktoken-exact path stays outside the node contract.
"""

from __future__ import annotations

from caveman.compress import compress
from caveman.tokens import estimate_tokens


def compress_text(text: str, level: int = 2) -> dict:
    """Compress prompt text to caveman speak at an explicit aggressiveness level."""
    result = compress(text, level=level)
    return {
        "text": result.compressed,
        "report": {
            "level": result.level,
            "original_tokens": result.original_tokens,
            "compressed_tokens": result.compressed_tokens,
            "saved_tokens": result.saved_tokens,
            "percent_saved": result.percent_saved,
        },
    }


def estimate_token_count(text: str) -> int:
    """Estimate the LLM token count of text without any tokenizer dependency."""
    return estimate_tokens(text)


NODES = [
    {
        "fn": compress_text,
        "id": "amarel.caveman.compress-text",
        "capabilities": ["text.compress-stopwords"],
        "summary": (
            "Compress prompt text by dropping filler words at an explicit "
            "aggressiveness level while protecting negations, code spans, and "
            "technical tokens."
        ),
        "inputs": [
            {"name": "text", "type_id": "amarel.text",
             "description": "Prompt text to compress."}
        ],
        "outputs": [
            {"name": "text", "type_id": "amarel.text",
             "description": "Compressed text."},
            {"name": "report", "type_id": "amarel.report",
             "description": "Token counts and savings for the compression."},
        ],
        "parameters": [
            {"name": "level", "value_type": "integer", "default": 2,
             "required": False, "choices": [1, 2, 3],
             "description": "Aggressiveness: 1 filler only, 2 + articles, 3 + auxiliaries."}
        ],
        "effects": [],
        "determinism": "deterministic",
        "idempotency": "idempotent",
        "tags": ["license.mit", "runtime.python", "dependency-free"],
        "postconditions": [
            "negation words, code spans, and technical tokens are never dropped"
        ],
    },
    {
        "fn": estimate_token_count,
        "id": "amarel.caveman.estimate-tokens",
        "capabilities": ["text.estimate-tokens"],
        "summary": "Estimate the LLM token count of text without any tokenizer dependency.",
        "inputs": [
            {"name": "text", "type_id": "amarel.text",
             "description": "Text to measure."}
        ],
        "outputs": [
            {"name": "count", "type_id": "amarel.integer",
             "description": "Estimated token count (max of words and chars/4)."}
        ],
        "parameters": [],
        "effects": [],
        "determinism": "deterministic",
        "idempotency": "idempotent",
        "tags": ["license.mit", "runtime.python", "dependency-free"],
    },
]
