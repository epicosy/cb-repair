#!/usr/bin/env bash

DIR=$(cd "$(dirname ${BASH_SOURCE[0]})" && pwd)

for chal in $DIR/lib/challenges/*/; do
    challenge_name="$(basename "$chal")"

    ./src/cb_repair.py genpolls -cn "$challenge_name" -n 1
done
