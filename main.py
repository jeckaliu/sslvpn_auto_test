from __future__ import annotations

import argparse
import asyncio

from web_auto.config import load_config
from web_auto.runner import WebAutomationRunner


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Config-driven web admin automation with Playwright"
    )
    parser.add_argument("--config", required=True, help="Path to YAML config file")
    parser.add_argument(
        "--flow",
        required=False,
        help="Only run one named flow from config",
    )
    return parser.parse_args()


async def _main() -> None:
    args = parse_args()
    config = load_config(args.config)
    runner = WebAutomationRunner(config=config, config_path=args.config)
    await runner.run(flow_name=args.flow)


if __name__ == "__main__":
    asyncio.run(_main())
