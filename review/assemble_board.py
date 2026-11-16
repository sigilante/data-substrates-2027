"""Embed review-data.json into review-template.html -> migration-review-board.html.

The board is the interface the author used to adjudicate each item.  Opened
locally (outside claude.ai) it is a read-only browser: every item with both
agents' judgements and the diff that introduced it.  The author's decisions
are in export/decisions/ and data/steps-adjudicated.csv.
"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(HERE, "review-data.json")))
page = open(os.path.join(HERE, "review-template.html")).read()
open(os.path.join(HERE, "migration-review-board.html"), "w").write(page.replace("__DATA__", json.dumps(data).replace("</", "<\\/")))
print(len(data), "items")
