"""
This script takes in a JSON history, and displays it in a readable format
"""

import json
import sys

if len(sys.argv) != 2:
    print("Please provide the input JSON file!")
    exit(1)

if not sys.argv[1].endswith(".json"):
    print("The input file must be a JSON file!")
    exit(1)

with open(sys.argv[1], "r") as f:
    board_str = f.read()

try:
    board = json.loads(board_str)
except:
    print("The board is not parsable.")
    exit(1)

for row in board:
    print(row)

exit(0)