"""CLI entry point: `python -m src.run --benchmark ... --llm ... --run-name ...`."""

import argparse

from src.benchmarks.swebench.run_swebench import SweBenchConfig, run
from src.types import RunInput


def _slice(value: str) -> tuple[int, int] | None:
    if value.lower() in {"", "none", "all"}:
        return None
    start, _, end = value.partition(":")
    return int(start or 0), int(end)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name, field in RunInput.model_fields.items():
        required = field.is_required()
        parser.add_argument(
            f"--{name.replace('_', '-')}",
            type=(
                _slice
                if name == "slice"
                else (int if field.annotation is int else str)
            ),
            required=required,
            default=None if required else field.default,
            help=f"default: {field.default}" if not required else None,
        )

    run(RunInput(**vars(parser.parse_args())), SweBenchConfig())


if __name__ == "__main__":
    main()
