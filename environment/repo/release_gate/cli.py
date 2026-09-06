from __future__ import annotations

import argparse
import json
import sys

from release_gate.decide import decide_from_bundle


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="release-gate")
    sub = parser.add_subparsers(dest="cmd", required=True)

    decide_p = sub.add_parser("decide", help="ship/block a release bundle")
    decide_p.add_argument("--bundle", required=True, help="path to bundle dir")
    decide_p.add_argument(
        "--json",
        action="store_true",
        help="print decision json on stdout",
    )

    args = parser.parse_args(argv)
    if args.cmd == "decide":
        decision = decide_from_bundle(args.bundle)
        if args.json:
            print(json.dumps(decision.to_dict(), indent=2))
        else:
            status = "SHIP" if decision.ship else "BLOCK"
            print(status)
            for reason in decision.reasons:
                print(f"- {reason}")
        return 0 if decision.ship else 1

    parser.error(f"unknown command: {args.cmd}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
