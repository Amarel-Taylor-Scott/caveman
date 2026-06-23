"""caveman CLI — compress prompts/context and report token savings."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .__version__ import __version__
from .compress import compress
from .tokens import count_tokens


def _read(path: str) -> str:
    return sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")


def cmd_compress(args: argparse.Namespace) -> int:
    text = _read(args.path)
    result = compress(text, level=args.level, exact_tokens=args.exact)
    if args.out:
        Path(args.out).write_text(result.compressed + "\n", encoding="utf-8")
    else:
        print(result.compressed)
    if args.stats or args.out:
        print(
            f"[caveman] level {result.level}: "
            f"{result.original_tokens} → {result.compressed_tokens} tokens "
            f"({result.saved_tokens} saved, {result.percent_saved}%)",
            file=sys.stderr,
        )
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    text = _read(args.path)
    result = compress(text, level=args.level, exact_tokens=args.exact)
    print(f"chars:             {len(text)}")
    print(f"original tokens:   {result.original_tokens}")
    print(f"compressed tokens: {result.compressed_tokens}  (level {result.level})")
    print(f"saved:             {result.saved_tokens} ({result.percent_saved}%)")
    return 0


def cmd_version(_: argparse.Namespace) -> int:
    print(f"caveman {__version__}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="caveman",
                                description="Compress prompts/context (talk like a caveman) and report token savings")
    p.add_argument("-V", "--version", action="version", version=f"%(prog)s {__version__}")
    sub = p.add_subparsers(dest="command")

    pc = sub.add_parser("compress", help="Compress a file (or '-' for stdin)")
    pc.add_argument("path")
    pc.add_argument("--level", type=int, default=2, choices=[1, 2, 3], help="1 light, 2 medium, 3 aggressive")
    pc.add_argument("--exact", action="store_true", help="Use tiktoken for exact token counts (needs extra)")
    pc.add_argument("--stats", action="store_true", help="Print savings to stderr")
    pc.add_argument("--out", default="", help="Write compressed text to this path")
    pc.set_defaults(func=cmd_compress)

    ps = sub.add_parser("stats", help="Report token counts & savings without printing the text")
    ps.add_argument("path")
    ps.add_argument("--level", type=int, default=2, choices=[1, 2, 3])
    ps.add_argument("--exact", action="store_true")
    ps.set_defaults(func=cmd_stats)

    sub.add_parser("version", help="Print version").set_defaults(func=cmd_version)
    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if not getattr(args, "command", None):
        parser.print_help()
        sys.exit(0)
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
