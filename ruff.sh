#!/bin/bash

set -e

RUFF_PKG=ruff@0.12.0
RUFF="uvx ${RUFF_PKG}"

if [ "$#" -eq 0 ]; then
    # No arguments: check the entire codebase
    targets="linux-russian-roulette.py"
else
    # Arguments given: check only those files
    targets="$@"
fi

$RUFF format $targets && $RUFF check --fix $targets && $RUFF check --select I --fix $targets
