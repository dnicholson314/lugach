import os
import sys

if getattr(sys, "frozen", False):
    os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", "0")

from lugach.cli.entrypoint import cli

if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.argv.extend(["app", "-i"])
    cli()


