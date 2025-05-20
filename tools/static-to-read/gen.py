# You can invoke this script with `uv run` (v0.3+):
#
#     uv run tools/static-to-read/gen.py
#
# /// script
# dependencies = [
#  "PyYAML==6.0.1",
# ]
# ///

import sys
import logging
import datetime
from pathlib import Path
import yaml


logger = logging.getLogger("gen")
logging.basicConfig(level=logging.DEBUG)

HERE = Path(__file__).parent
ROOT = HERE.parent.parent
CONTENT = ROOT / "content"
LINKS_DIR = CONTENT / "links"

now = datetime.datetime.now()

# Read markdown files from links directory
links = []
for file_path in LINKS_DIR.glob("*.md"):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        if not content.startswith("---"):
            continue

        frontmatter_end = content.find("---", 3)
        if frontmatter_end == -1:
            continue

        frontmatter_yaml = content[3:frontmatter_end].strip()
        metadata = yaml.safe_load(frontmatter_yaml)

        tags = metadata.get("tags", [])
        if "to-read" not in tags:
            continue

        date_str = metadata.get("date")
        if not date_str:
            continue

        date = datetime.datetime.fromisoformat(date_str)
        url = metadata.get("params", {}).get("url")
        title = metadata.get("title")
        if not url or not title:
            continue

        links.append({"date": date, "url": url, "title": title})

links.sort(key=lambda x: x["date"], reverse=True)
recent = links[:5]

print("<ol class='to-read'>")
for link in recent:
    print(f"  <li class='entry'><a href='{link["url"]}'>{link["title"]}</a></li>")
print("</ol>")
print(f"<p class='to-read-metadata-generated'>generated: {now.strftime('%B %d, %Y at %H:%M:%S')}</p>")
       
sys.exit(0)
