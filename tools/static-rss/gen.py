# You can invoke this script with `uv run` (v0.3+):
#
#     uv run tools/static-rss/gen.py
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
from typing import Iterator, Optional
from pathlib import Path
from xml.etree import ElementTree
from dataclasses import dataclass

import markdown
import requests
import html2text
import feedparser
import dateutil.parser


logger = logging.getLogger("gen")
logging.basicConfig(level=logging.DEBUG)


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
            logger.warn("failed to fetch: %s", self.title, exc_info=True)
            return

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


                yield Entry(
                    timestamp=dateutil.parser.parse(entry.published if "published" in entry else entry.updated),
                    title=entry.title,
                    link=entry.link,
                    content=content_html,
                    feed=self,
                )

            elif self.category == "mastodon":
                # mastodon post RSS feed

                content_md = html2text.html2text(entry.summary)
                content_html = markdown.markdown(content_md)
            
                yield Entry(
                    timestamp=dateutil.parser.parse(entry.published if "published" in entry else entry.updated),
                    # use first line of content
                    title=content_md.partition("\n")[0],
                    link=entry.link,
                    content=content_html,
                    feed=self,
                )

            else:
                raise ValueError("unexpected category")


feeds = [
    Feed.from_mastodon("@cxiao@infosec.exchange"),
    Feed.from_mastodon("@malcat@infosec.exchange"),
    Feed.from_mastodon("@pnx@infosec.exchange"),
    Feed.from_mastodon("@trailofbits@infosec.exchange"),
    Feed.from_mastodon("@HexRaysSA@infosec.exchange"),
    Feed.from_mastodon("@binaryninja@infosec.exchange"),
]


tree = ElementTree.fromstring(Path(sys.argv[1]).read_text(encoding="utf-8"))
for node in tree.findall('.//outline[@title="a-quiet"]/outline[@type="rss"]'):
    feeds.append(
        Feed(
            category="rss",
            title=node.attrib.get("title"),
            url=node.attrib.get("xmlUrl"),
            homepage=node.attrib.get("htmlUrl"),
        )
    )


# take the 20 most recently updated repos
for repo in requests.get("https://api.github.com/users/williballenthin/starred?sort=updated&direction=desc&per_page=20").json():
    title = repo["full_name"]
    logger.debug("found repo: %s", title)

    homepage = f"https://github.com/{title}"
    url = homepage + "/releases.atom"
    feeds.append(
        Feed("release", url, homepage=homepage, title=title)
    )

# TODO
# feeds = feeds[:3]

entries = []
for feed in feeds:
    entries.extend(feed.fetch())


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
                     <span class="feed"><a href="{entry.feed.homepage}">{entry.feed.title}</a></span>
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
       
