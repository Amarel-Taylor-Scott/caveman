# Contributing

Thanks for helping improve **caveman**!

## Dev setup

```bash
pip install -e ".[dev]"
pytest -q                    # runs fully offline
```

## Where things live

- **Compression rules / word sets** -> `caveman/compress.py`
- **Token estimation** -> `caveman/tokens.py`
- **CLI** -> `caveman/cli.py`

The safety invariant is sacred: never drop numbers, code spans, URLs, capitalized
words, or negations. Any new rule must keep `test_facts_preserved_*` green.

## Quality bar

- Add/extend tests in `tests/`; `pytest -q` passes; `python -m compileall caveman` clean.
- Keep the core dependency-free (tiktoken stays an optional extra).
