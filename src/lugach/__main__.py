import sys

from lugach.cli.entrypoint import cli

if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.argv.extend(["app", "-i"])
    cli()

