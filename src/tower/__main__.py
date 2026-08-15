"""Module entrypoint with a real activation command."""
from __future__ import annotations
import sys
if len(sys.argv) > 1 and sys.argv[1] == "activate":
    from .activation_cli import main
    raise SystemExit(main(sys.argv[2:]))
from .cli import main
raise SystemExit(main())
