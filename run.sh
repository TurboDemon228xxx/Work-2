#!/usr/bin/env sh
cd "$(dirname "$0")" || exit
exec "${WORK2_PYTHON:-python3}" -m src "$@"
