# You can invoke this script with `uv run` (v0.3+):
#
#     uv run tools/static-rss/gen.py /path/to/opml
#
# /// script
# dependencies = [
#  "feedparser==6.0.11",
#  "html2text==2024.2.26",
#  "markdown==3.7",
#  "python-dateutil==2.9.0.post0",
#  "requests==2.32.3",
# ]
# ///

import sys
import html
import logging
import datetime
import itertools
import urllib.error
import concurrent.futures
from pathlib import Path
from typing import Iterator, Optional
from dataclasses import dataclass

import markdown
import requests
import html2text
import feedparser
import dateutil.parser
import xml.etree.ElementTree as ET


logger = logging.getLogger("gen")
logging.basicConfig(level=logging.DEBUG)


def parse_opml(opml_path):
    """Parse OPML file directly to extract feeds with all necessary information"""
    tree = ET.parse(opml_path)
    root = tree.getroot()
    
    # Find the "a-quiet" outline group
    quiet_outline = None
    for outline in root.findall('.//outline'):
        if outline.get("title") == "a-quiet" or outline.get("text") == "a-quiet":
            quiet_outline = outline
            break
    
    if quiet_outline is None:
        logger.warning("Could not find 'a-quiet' section in OPML")
        return []
    
    # Find all RSS feeds within the a-quiet section
    feeds = []
    rss_outlines = quiet_outline.findall('./outline[@type="rss"]')
    
    for outline in rss_outlines:
        xml_url = outline.get("xmlUrl")
        html_url = outline.get("htmlUrl")
        title = outline.get("title") or outline.get("text")
        
        if xml_url and title:
            feed_data = {
                "url": xml_url,
                "title": title,
                "homepage": html_url,
                "tags": ["a-quiet"]  # All feeds in this section have this tag
            }
            feeds.append(feed_data)
    
    return feeds


# Parse OPML file completely with direct XML parsing
opml_feeds = parse_opml(Path(sys.argv[1]))


@dataclass
class Entry:
    timestamp: datetime.datetime
    title: str
    link: str
    content: str
    feed: "Feed"


@dataclass
class Feed:
    category: str
    url: str
    title: str

    # link to project/homepage/base, not the feed
    homepage: Optional[str] = None

    @classmethod
    def from_mastodon(cls, handle):
        assert handle[0] == "@"
        assert "@" in handle[1:]

        user, _, server = handle.rpartition("@")

        return cls(
            category="mastodon",
            # returns last 20 posts by default
            url=f"https://{server}/{user}.rss",
            homepage=f"https://{server}/{user}",
            title=handle
        )

    def fetch(self) -> Iterator[Entry]:
        logger.debug("fetching feed: %s", self.title)

        try:
            d = feedparser.parse(self.url)
        except Exception as e:
            logger.error("failed to fetch feed %s: %s", self.title, e, exc_info=True)
            return

        # Check for feed parsing errors
        if hasattr(d, 'bozo') and d.bozo and hasattr(d, 'bozo_exception'):
            logger.error("failed to parse feed %s: %s", self.title, d.bozo_exception)
            
        # Track entries for logging
        total_entries = len(d.entries)
        entries_in_period = 0
        now = datetime.datetime.now()
        three_days_ago = (now - datetime.timedelta(days=3)).date()

        for entry in d.entries:

            if self.category == "rss" or self.category == "release":
                # github releases Atom feed

                if hasattr(entry, "content"):
                    for content in entry.content:
                        if content.type in ("text/html", "application/xhtml+xml"):

                            # danger: injection
                            # content_html = html.unescape(content.value)

                            content_md = html2text.html2text(content.value)
                            content_html = markdown.markdown(content_md)

                        elif content.type == "text/plain":
                            content_html = markdown.markdown(content.value)

                        else:
                            raise ValueError("unexpected content type: " + content.type)

                        # only yield one entry per entry
                        break

                elif hasattr(entry, "summary"):
                    content_html = markdown.markdown(entry.summary)

                elif hasattr(entry, "title"):
                    content_html = "<i>(empty)</i>"

                else:
                    logger.warning("post has no content")
                    content_html = "<i>(empty)</i>"

                ts = entry.published if "published" in entry else entry.updated
                # handle:
                #
                #     dateutil.parser._parser.ParserError: hour must be in 0..23: Fri, 22 Nov 2024 24:00:00 GMT
                #
                # this is probably technically not correct, since it backdates the post by a day, but whatever.
                ts = ts.replace(" 24:00:00", " 00:00:00")

                entry_obj = Entry(
                    timestamp=dateutil.parser.parse(ts),
                    title=entry.title,
                    link=entry.link,
                    content=content_html,
                    feed=self,
                )
                
                # Check if entry is within the 3-day period for logging
                entry_date = entry_obj.timestamp.date() if entry_obj.timestamp.tzinfo is None else entry_obj.timestamp.astimezone().date()
                if entry_date >= three_days_ago:
                    entries_in_period += 1
                
                yield entry_obj

            elif self.category == "mastodon":
                # mastodon post RSS feed

                content_md = html2text.html2text(entry.summary)
                content_html = markdown.markdown(content_md)
            
                entry_obj = Entry(
                    timestamp=dateutil.parser.parse(entry.published if "published" in entry else entry.updated),
                    # use first line of content
                    title=content_md.partition("\n")[0],
                    link=entry.link,
                    content=content_html,
                    feed=self,
                )
                
                # Check if entry is within the 3-day period for logging
                entry_date = entry_obj.timestamp.date() if entry_obj.timestamp.tzinfo is None else entry_obj.timestamp.astimezone().date()
                if entry_date >= three_days_ago:
                    entries_in_period += 1
                
                yield entry_obj

            else:
                raise ValueError("unexpected category")
        
        # Log feed statistics
        logger.info("feed %s: found %d total entries, %d entries in past 3 days", 
                   self.title, total_entries, entries_in_period)


feeds = [
    Feed.from_mastodon("@cxiao@infosec.exchange"),
    Feed.from_mastodon("@malcat@infosec.exchange"),
    Feed.from_mastodon("@pnx@infosec.exchange"),
    Feed.from_mastodon("@trailofbits@infosec.exchange"),
    Feed.from_mastodon("@HexRaysSA@infosec.exchange"),
    Feed.from_mastodon("@binaryninja@infosec.exchange"),
]


for feed in opml_feeds:
    feeds.append(
        Feed(
            category="rss",
            title=feed["title"],
            url=feed["url"],
            homepage=feed["homepage"],
        )
    )


# take the 20 most recently updated repos
try:
    response = requests.get("https://api.github.com/users/williballenthin/starred?sort=updated&direction=desc&per_page=20")
    if response.status_code == 200:
        repos = response.json()
        
        for repo in repos:
            title = repo["full_name"]
            logger.debug("found repo: %s", title)

            homepage = f"https://github.com/{title}"
            url = homepage + "/releases.atom"
            feeds.append(
                Feed("release", url, homepage=homepage, title=title)
            )
    else:
        logger.warning("failed to fetch GitHub starred repos: HTTP %d", response.status_code)
except Exception as e:
    logger.warning("failed to fetch GitHub starred repos: %s", e, exc_info=True)

# TODO
# feeds = feeds[:3]

entries = []
with concurrent.futures.ThreadPoolExecutor(max_workers=32) as executor:
    def doit(feed):
        return list(feed.fetch())

    futures = [executor.submit(doit, feed) for feed in feeds]
    for future in concurrent.futures.as_completed(futures):
        entries.extend(future.result())

# this nightly release is updated every day
# ghostty-org/ghostty
entries = [e for e in entries 
           if "Ghostty Tip" not in e.title]

# only show entries within the past three days
now = datetime.datetime.now()
three_days_ago = (now - datetime.timedelta(days=3)).date()
# TODO
entries = list(filter(lambda entry: entry.timestamp.date() >= three_days_ago, entries))

print("<ol class='feed'>")
entries = [entry for entry in entries if entry.timestamp.tzinfo is not None] 
entries.sort(key=lambda f: f.timestamp, reverse=True)
for day, entries in itertools.groupby(entries, lambda entry: entry.timestamp.date()):
    print(f"""
      <li><span class="date">{day.strftime("%B %d, %Y")}</span>
          <ol class="date-entries">
    """)

    for entry in entries:
        print(f"""
          <li class="entry">
              <details>
                 <summary>
                     <span class="link"><a href="{entry.link}">🔗</a></span>
                     <span class="feed">{f'<a href="{entry.feed.homepage}">{entry.feed.title}</a>' if entry.feed.homepage else entry.feed.title}</span>
                     <span class="title">{entry.title}</span>
                     <span class="category">{entry.feed.category}</span>
                 </summary>

                 <div class="content">
                     {entry.content}
                 </div>
              </details>
          </li>
        """)

    print("</ol>")

print("</ol>")
print(f"<p class='feed-metadata-generated'>generated: {now.strftime('%B %d, %Y at %H:%M:%S')}</p>")
       
