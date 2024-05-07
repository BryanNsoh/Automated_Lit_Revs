import sys
import os

if sys.platform == "win32":
    os.environ.setdefault("GUNICORN_CMD_ARGS", "--log-level=debug")
