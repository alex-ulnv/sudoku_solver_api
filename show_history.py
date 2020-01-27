"""
This script takes in a JSON board, and displays it in a readable format
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
    history_str = f.read()

try:
    history_items = json.loads(history_str)
except:
    print("The file is not parsable.")
    exit(1)

for history_item in history_items:
    print("Printing history in descending order:")
    print("Item:")
    for k,v in history_item.items():
        print("\t{}:\t{}".format(k, v))

exit(0)