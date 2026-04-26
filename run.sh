#!/bin/sh

set -e # Exit early if any commands fail

# Copied from .codecrafters/run.sh

SCRIPT_DIR="$(dirname "$0")"
PID_FILE="$HOME/.crafterscode/background.pid"

if [ "$1" = "background" ]; then
    echo $$ > "$PID_FILE"
fi

PYTHONSAFEPATH=1 PYTHONPATH="$SCRIPT_DIR" exec uv run \
--project "$SCRIPT_DIR" \
-m app.main \
"$@"

