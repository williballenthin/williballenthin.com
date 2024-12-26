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
from typing import Iterator, Optional
from dataclasses import dataclass

import pinboard


logger = logging.getLogger("gen")
logging.basicConfig(level=logging.DEBUG)

now = datetime.datetime.now()
try:
    pb = pinboard.Pinboard(os.environ["PINBOARD_TOKEN"])
   except urllib.error.URL

# take the five most recent posts
posts = pb.posts.recent()["posts"]
toread = list(post for post in posts if post.toread)
recent = list(toread[:5])

print("<ol class='to-read'>")
for post in recent:
   print(f"  <li class='entry'><a href='{post.url}'>{post.description}</a></li>")
print("</ol>")
print(f"<p class='to-read-metadata-generated'>generated: {now.strftime('%B %d, %Y at %H:%M:%S')}</p>")
       
sys.exit(0)
