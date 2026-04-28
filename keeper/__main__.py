"""Allow `python -m keeper` to invoke the CLI."""
import sys
from keeper.checkpoint import main

if __name__ == "__main__":
    sys.exit(main())
