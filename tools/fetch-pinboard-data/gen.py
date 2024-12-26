# You can invoke this script with `uv run` (v0.3+):
#
#     uv run tools/static-to-read/gen.py
#
# /// script
# dependencies = [
#  "pinboard==2.1.9",
# ]
# ///

import os
import sys
import logging
import datetime
import itertools
import urllib.error
from typing import Iterator, Optional
from dataclasses import dataclass

import pinboard


logger = logging.getLogger("gen")
logging.basicConfig(level=logging.DEBUG)

now = datetime.datetime.now()
try:
    pb = pinboard.Pinboard(os.environ["PINBOARD_TOKEN"])
except urllib.error.URLError:
	

# take the five most recent posts
response = pb.posts.all(parse_response=False)
print(response.read().decode("utf-8"))
       
sys.exit(0)
