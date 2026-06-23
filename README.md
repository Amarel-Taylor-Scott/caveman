# 🪨 caveman

[![CI](https://github.com/Amarel-Taylor-Scott/caveman/actions/workflows/ci.yml/badge.svg)](https://github.com/Amarel-Taylor-Scott/caveman/actions/workflows/ci.yml)
![python](https://img.shields.io/badge/python-3.10%2B-blue)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**why use many token when few token do trick.**

`caveman` compresses prompts and context for LLMs by stripping predictable
grammar and filler — articles, politeness, hedges, low-information auxiliaries —
so you send fewer tokens for the same meaning. It's deterministic, pure-stdlib,
and reports exactly how much you saved.

**The safety rule:** it never drops information. Numbers, code spans, URLs/emails,
capitalized words (proper nouns / acronyms), and **negations** (`not`, `no`,
`never`, `without`, …) are always preserved. Compression is lossy on grammar,
never on facts.

## Install

```bash
pip install -e .                  # core (stdlib only)
pip install -e '.[tiktoken]'      # add exact token counts
```

## Quick start

```bash
caveman compress prompt.txt --level 2 --out small.txt
echo "Could you please just summarize the report for me?" | caveman compress - --level 3 --stats
caveman stats prompt.txt --level 3
```

Example (`--level 3 --stats`):

```
[caveman] level 3: 36 → 25 tokens (11 saved, 30.6%)
Could you summarize report? Dr. Smith wants $10,000 figure and 42% increase. Do not skip deadline.
```

Note what survived: `Dr. Smith`, `$10,000`, `42%`, and the negation `not`.

## Levels

| Level | Drops | Use when |
|-------|-------|----------|
| 1 (light)  | filler & politeness (`basically`, `really`, `please`, …) | safest, readable |
| 2 (medium) | + articles & soft hedges (`a/an/the`, `usually`, `maybe`) | good default |
| 3 (aggressive) | + low-info auxiliaries & prepositions (`is/are`, `of/to/in`, …) | max savings, telegraphic |

## Use it as a library

```python
from caveman import compress

r = compress(open("prompt.txt", encoding="utf-8").read(), level=2)
print(r.compressed)
print(r.original_tokens, "→", r.compressed_tokens, f"({r.percent_saved}% saved)")
```

`compress(text, level=1..3, exact_tokens=False)` returns a `Compression` with
`.compressed`, `.original_tokens`, `.compressed_tokens`, `.saved_tokens`,
`.percent_saved`.

## How it protects facts

- Tokens with digits / `/` / `@` / `_` / `://` → kept (numbers, paths, URLs, ids).
- Capitalized words → kept (proper nouns, acronyms).
- ``` `code spans` ``` → kept **verbatim**.
- Negations → always kept (so "do not deploy" never becomes "do deploy").

## Caveats

This is *lossy* compression for **LLM input** — it trades grammatical polish for
tokens. Don't use it on text meant for humans, and review aggressive (level 3)
output on critical prompts.

## License

[MIT](LICENSE) © Amarel Taylor Scott.
