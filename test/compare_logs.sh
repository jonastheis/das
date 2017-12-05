#!/usr/bin/env bash

cat $1 | sed 's/^............................//' > $1_raw
cat $2 | sed 's/^............................//' > $2_raw

diff $1_raw $2_raw