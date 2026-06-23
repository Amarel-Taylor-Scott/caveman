# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-06-22

### Added
- Deterministic prompt/context compressor with three levels (filler/politeness →
  + articles/hedges → + low-info auxiliaries/prepositions).
- Fact-safety guarantees: numbers, code spans, URLs/emails, capitalized words, and
  negations are always preserved; sentence punctuation is salvaged.
- Token estimation (heuristic; exact via optional `tiktoken` extra) and a savings
  report.
- `caveman` CLI: `compress`, `stats`, `version`. 8 offline tests + CI.
