# You can invoke this script with `uv run` (v0.3+):
#
#     uv run tools/fetch-pinboard-data/sync-pinboard-links.py
#
# /// script
# dependencies = [
#  "pinboard==2.1.9",
#  "PyYAML==6.0.1",
# ]
# ///

import os
import sys
import logging
import datetime
import urllib.error
from pathlib import Path
import json
import yaml

import pinboard


logger = logging.getLogger("sync-pinboard-links")
logging.basicConfig(level=logging.DEBUG)

HERE = Path(__file__).parent
ROOT = HERE.parent.parent
CONTENT = ROOT / "content"
LINKS_DIR = CONTENT / "links"


now = datetime.datetime.now()
try:
    # Skip API call if no token is provided
    if "PINBOARD_TOKEN" not in os.environ:
        logger.error("PINBOARD_TOKEN environment variable not set")
        sys.exit(1)

    pb = pinboard.Pinboard(os.environ["PINBOARD_TOKEN"])
    response = pb.posts.all(parse_response=False)
except urllib.error.URLError:
    logger.warning("pinboard is down")
    sys.exit(0)
else:
    entries = json.loads(response.read().decode("utf-8"))
    for entry in entries:
        # each entry is like:
        #
        #     {
        #         "href": "https://cxiao.net/posts/2023-12-08-rust-reversing-panic-metadata/",
        #         "description": "Using panic metadata to recover source code information from Rust binaries | cxiao.net",
        #         "extended": "",
        #         "meta": "0bbdcc122e81c1e03d0540e68222d502",
        #         "hash": "f6c4b63b2cb24df3777d7769e167a7c0",
        #         "time": "2024-01-31T21:40:00Z",
        #         "shared": "yes",
        #         "toread": "no",
        #         "tags": "rust reverse-engineering"
        #     }
        
        # skip private entries
        if entry.get("shared", "yes").lower() != "yes":
            continue
            
        timestamp = datetime.datetime.strptime(entry["time"], "%Y-%m-%dT%H:%M:%SZ")
        # add timezone to make it consistent with example format (e.g. +0200)
        timestamp = timestamp.replace(tzinfo=datetime.timezone.utc)
        timestamp_str = timestamp.strftime("%Y%m%dT%H%M%S")
        filename = f"{timestamp_str}.md"
        file_path = LINKS_DIR / filename
        
        if file_path.exists():
            logger.debug(f"skipping existing: {file_path.relative_to(ROOT)}")
            continue
            
        tags = [tag.strip() for tag in entry.get("tags", "").split()] 
        if entry.get("toread", "").lower() == "yes":
            tags.append("to-read")
            
        frontmatter = {
            "title": entry["description"],
            "slug": timestamp_str,
            "date": timestamp.strftime('%Y-%m-%dT%H:%M:%S%z'),
            "params": {
                "url": entry['href']
            },
            "tags": tags
        }
        
        yaml_content = yaml.dump(frontmatter, sort_keys=False, default_flow_style=False, allow_unicode=True, width=1000)
        
        content = f"---\n{yaml_content}---"
        if entry.get("extended", "").strip():
            content += f"\n\n{entry['extended']}\n"
            
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        logger.info(f"link: {file_path.relative_to(ROOT)}: {entry['description']}")

    sys.exit(0)
