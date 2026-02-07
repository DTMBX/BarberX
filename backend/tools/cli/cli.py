"""Minimal evidence CLI using argparse. Phase 1 scaffold only."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .exporter import export_case
from .ffmpeg_proxy import create_video_proxy
from .hashing import compute_sha256, iter_files
from .manifest import create_manifest
from .verifier import verify_manifest


def cmd_hash(args: argparse.Namespace) -> int:
    src = Path(args.input_dir)
    if not src.exists():
        print("Input directory not found", file=sys.stderr)
        return 2
    out = Path(args.out) if args.out else Path.cwd()
    out.mkdir(parents=True, exist_ok=True)

    # simple: compute hashes for all files under input_dir and write a small index
    index = []
    for p in iter_files(src):
        index.append(
            {
                "path": str(p.relative_to(src)),
                "sha256": compute_sha256(p),
                "size": p.stat().st_size,
            }
        )

    import json

    with (out / "hash_index.json").open("w", encoding="utf-8") as fh:
        json.dump({"items": index}, fh, indent=2)

    print(f"Wrote hash_index.json to {out}")
    return 0


def cmd_manifest(args: argparse.Namespace) -> int:
    case_dir = Path(args.case_dir)
    try:
        m = create_manifest(case_dir)
        print(f"Created canonical manifest with {len(m.get('originals', []))} originals")
        return 0
    except Exception as e:
        print(str(e), file=sys.stderr)
        return 2


def cmd_proxy(args: argparse.Namespace) -> int:
    case_dir = Path(args.case_dir)
    try:
        out_path, sha = create_video_proxy(case_dir, args.original_rel_path, preset=args.preset)
        print(f"Created proxy: {out_path} sha256={sha}")
        return 0
    except Exception as e:
        print(f"Proxy error: {e}", file=sys.stderr)
        return 2


def cmd_export(args: argparse.Namespace) -> int:
    case_dir = Path(args.case_dir)
    out_zip = Path(args.out)
    try:
        export_case(case_dir, out_zip, normalize_mtime=args.normalize_mtime)
        print(f"Wrote export: {out_zip}")
        return 0
    except Exception as e:
        print(f"Export error: {e}", file=sys.stderr)
        return 2


def cmd_verify(args: argparse.Namespace) -> int:
    case_dir = Path(args.case_dir)
    try:
        res = verify_manifest(case_dir)
        print(res)
        if res.get("missing") or res.get("mismatches"):
            return 3
        return 0
    except Exception as e:
        print(f"Verify error: {e}", file=sys.stderr)
        return 2


def main(argv=None):
    p = argparse.ArgumentParser(prog="evident")
    sub = p.add_subparsers(dest="cmd")

    h = sub.add_parser("hash")
    h.add_argument("input_dir")
    h.add_argument("--out")
    h.set_defaults(func=cmd_hash)

    m = sub.add_parser("manifest")
    m.add_argument("case_dir")
    m.set_defaults(func=cmd_manifest)

    proxy_p = sub.add_parser("proxy")
    proxy_p.add_argument("case_dir")
    proxy_p.add_argument("original_rel_path")
    proxy_p.add_argument("--preset", choices=["web", "review"], default="web")
    proxy_p.set_defaults(func=cmd_proxy)

    e = sub.add_parser("export")
    e.add_argument("case_dir")
    e.add_argument("--out", required=True)
    e.add_argument("--normalize-mtime", action="store_true")
    e.set_defaults(func=cmd_export)

    v = sub.add_parser("verify")
    v.add_argument("case_dir")
    v.set_defaults(func=cmd_verify)

    args = p.parse_args(argv)
    if not hasattr(args, "func"):
        p.print_help()
        return 1
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
