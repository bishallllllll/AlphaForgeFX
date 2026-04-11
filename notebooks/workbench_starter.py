"""Starter script for Jupyter/Lab-style iterative debugging.

Run this file directly or copy cells into a notebook.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tradingagents.workbench import (
    load_environment,
    get_default_config_copy,
    apply_runtime_config,
    list_methods,
    list_tools,
    list_factories,
)


def main() -> None:
    # Part 1 bootstrap
    load_environment()
    cfg = get_default_config_copy()
    cfg["llm_provider"] = "openai"
    active = apply_runtime_config(cfg)

    print("Active provider:", active.get("llm_provider"))

    # Part 3/4/5 quick introspection
    print("Data methods:", list_methods())
    print("Tools:", list_tools())
    print("Agent factories:", list_factories())


if __name__ == "__main__":
    main()
