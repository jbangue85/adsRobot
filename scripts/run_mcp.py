#!/usr/bin/env python3
"""Run the MCP server from the repository checkout."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from meta_ads_mcp.server import main


if __name__ == "__main__":
    main()
