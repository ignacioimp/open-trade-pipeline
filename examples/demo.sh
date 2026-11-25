#!/bin/sh
set -eu
# Use a new file; init will refuse to overwrite an existing file.
state=${1:-demo-state.json}
python pipeline.py --file "$state" init
python pipeline.py --file "$state" add DEMO-001 operator 2030-01-01
python pipeline.py --file "$state" done DEMO-001 1
python pipeline.py --file "$state" advance DEMO-001 'Diagnostic Started' --due 2030-01-02
python pipeline.py --file "$state" done DEMO-001 2
python pipeline.py --file "$state" advance DEMO-001 'Diagnostic Completed' --due 2030-01-03
python pipeline.py --file "$state" status --as-of 2030-01-04
python pipeline.py --file "$state" payment DEMO-001 DEMO-RECEIPT
python pipeline.py --file "$state" done DEMO-001 3
python pipeline.py --file "$state" advance DEMO-001 'Cost Estimate Started' --due 2030-01-05
python pipeline.py --file "$state" status --as-of 2030-01-04
