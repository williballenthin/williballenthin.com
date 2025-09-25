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
import re
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

# Configuration: Number of days to look back for recent entries
RECENT_DAYS = 3

# Global list to track feeds with no entries for summary
feeds_with_no_entries = []


def remove_heading_links(html_content):
    """
    Remove anchor links from headings (h1-h6) in HTML content.
    This preserves the heading text but removes any nested anchor links.
    Must handle both wrapped links and empty anchor tags that become problematic in markdown.
    """
    # Handle HTML anchor links that wrap heading text
    wrapped_link_pattern = r'(<h[1-6][^>]*>)\s*<a[^>]*>([^<]*)</a>\s*(</h[1-6]>)'
    
    def replace_wrapped_link(match):
        opening_tag = match.group(1)
        text_content = match.group(2)
        closing_tag = match.group(3)
        return f"{opening_tag}{text_content}{closing_tag}"
    
    content = re.sub(wrapped_link_pattern, replace_wrapped_link, html_content, flags=re.IGNORECASE)
    
    # Handle empty anchor tags within headings (critical for Rust Blog and similar)
    # Pattern: <h4 id="..."><a class="anchor" href="..."></a>\n text content</h4>
    empty_anchor_pattern = r'(<h[1-6][^>]*>)\s*<a[^>]*></a>\s*([\s\S]*?)(</h[1-6]>)'
    
    def replace_empty_anchor(match):
        opening_tag = match.group(1)
        text_content = match.group(2)
        closing_tag = match.group(3)
        # Clean up whitespace and newlines in the text content
        clean_text = re.sub(r'\s+', ' ', text_content.strip())
        return f"{opening_tag}{clean_text}{closing_tag}"
    
    content = re.sub(empty_anchor_pattern, replace_empty_anchor, content, flags=re.IGNORECASE | re.DOTALL)
    
    # Handle anchor links at the end of headings (common pattern: heading text <a href="#anchor">#</a>)
    # Pattern: <h4 id="...">text content<a href="...">link text</a></h4>
    trailing_anchor_pattern = r'(<h[1-6][^>]*>)([\s\S]*?)<a[^>]*>[^<]*</a>\s*(</h[1-6]>)'
    
    def replace_trailing_anchor(match):
        opening_tag = match.group(1)
        text_content = match.group(2)
        closing_tag = match.group(3)
        # Clean up whitespace and remove any remaining anchor artifacts
        clean_text = re.sub(r'\s+', ' ', text_content.strip())
        return f"{opening_tag}{clean_text}{closing_tag}"
    
    content = re.sub(trailing_anchor_pattern, replace_trailing_anchor, content, flags=re.IGNORECASE | re.DOTALL)
    
    return content


def clean_markdown_links_from_headings(html_content):
    """
    Clean up any malformed markdown links in headings after markdown processing.
    This handles cases where html2text->markdown conversion created problems.
    """
    # Pattern: heading with [](...) that may be broken across elements
    markdown_link_pattern = r'(<h[1-6][^>]*>)\s*\[\]\([^)]*\)\s*(.*?)(</h[1-6]>)'
    
    def replace_markdown_link(match):
        opening_tag = match.group(1)
        text_content = match.group(2)
        closing_tag = match.group(3)
        # Remove any remaining markup and clean text
        clean_text = re.sub(r'<[^>]*>', '', text_content).strip()
        return f"{opening_tag}{clean_text}{closing_tag}"
    
    content = re.sub(markdown_link_pattern, replace_markdown_link, html_content, flags=re.IGNORECASE | re.DOTALL)
    
    # Handle any remaining markdown link artifacts in headings
    # Pattern: heading with markdown link remnants like [text](url) or [](...)
    general_markdown_pattern = r'(<h[1-6][^>]*>)([\s\S]*?)\[[^\]]*\]\([^\)]*\)([\s\S]*?)(</h[1-6]>)'
    
    def replace_general_markdown(match):
        opening_tag = match.group(1)
        text_before = match.group(2)
        text_after = match.group(3)
        closing_tag = match.group(4)
        # Combine text content, removing the markdown link
        combined_text = (text_before + text_after).strip()
        clean_text = re.sub(r'<[^>]*>', '', combined_text).strip()
        clean_text = re.sub(r'\s+', ' ', clean_text)
        return f"{opening_tag}{clean_text}{closing_tag}"
    
    content = re.sub(general_markdown_pattern, replace_general_markdown, content, flags=re.IGNORECASE | re.DOTALL)
    
    return content


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
            # Use proper User-Agent headers, especially important for Reddit feeds
            if 'reddit.com' in self.url.lower():
                import requests
                headers = {
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                response = requests.get(self.url, headers=headers, timeout=30)
                response.raise_for_status()
                d = feedparser.parse(response.text)
            else:
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
        three_days_ago = (now - datetime.timedelta(days=RECENT_DAYS)).date()

        for entry in d.entries:

            if self.category == "rss" or self.category == "release":
                # github releases Atom feed

                if hasattr(entry, "content"):
                    for content in entry.content:
                        if content.type in ("text/html", "application/xhtml+xml"):

                            # danger: injection
                            # content_html = html.unescape(content.value)
                            
                            # Remove anchor links from headings before processing
                            cleaned_content = remove_heading_links(content.value)

                            content_md = html2text.html2text(cleaned_content)
                            content_html = markdown.markdown(content_md)
                            
                            # Clean up any remaining malformed markdown links in headings
                            content_html = clean_markdown_links_from_headings(content_html)
                            
                            # Fix any headings that got broken across elements
                            content_html = fix_broken_heading_elements(content_html)

                        elif content.type == "text/plain":
                            content_html = markdown.markdown(content.value)

                        else:
                            raise ValueError("unexpected content type: " + content.type)

                        # only yield one entry per entry
                        break

                elif hasattr(entry, "summary"):
                    # Remove anchor links from headings in summary as well
                    cleaned_summary = remove_heading_links(entry.summary)
                    content_html = markdown.markdown(cleaned_summary)
                    
                    # Clean up any remaining malformed markdown links in headings
                    content_html = clean_markdown_links_from_headings(content_html)
                    
                    # Fix any headings that got broken across elements
                    content_html = fix_broken_heading_elements(content_html)

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
                
                # Remove anchor links from headings before processing
                cleaned_summary = remove_heading_links(entry.summary)
                content_md = html2text.html2text(cleaned_summary)
                content_html = markdown.markdown(content_md)
                
                # Clean up any remaining malformed markdown links in headings
                content_html = clean_markdown_links_from_headings(content_html)
                
                # Fix any headings that got broken across elements
                content_html = fix_broken_heading_elements(content_html)
            
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
        logger.info("feed %s: found %d total entries, %d entries in past %d days", 
                   self.title, total_entries, entries_in_period, RECENT_DAYS)
        
        # Track feeds with no entries for summary
        if total_entries == 0 or entries_in_period == 0:
            feeds_with_no_entries.append({
                'title': self.title,
                'total_entries': total_entries,
                'recent_entries': entries_in_period,
                'url': self.url
            })


feeds = [
    Feed.from_mastodon("@cxiao@infosec.exchange"),
    Feed.from_mastodon("@malcat@infosec.exchange"),
    Feed.from_mastodon("@pnx@infosec.exchange"),
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
           if "Ghostty Tip" not in e.title
           and e.title != "nightly"]

# only show entries within the past three days
now = datetime.datetime.now()
three_days_ago = (now - datetime.timedelta(days=RECENT_DAYS)).date()
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

# Summarize feeds with no entries
if feeds_with_no_entries:
    logger.info("=== FEEDS WITH NO ENTRIES SUMMARY ===")
    no_total_entries = [f for f in feeds_with_no_entries if f['total_entries'] == 0]
    no_recent_entries = [f for f in feeds_with_no_entries if f['total_entries'] > 0 and f['recent_entries'] == 0]
    
    if no_total_entries:
        logger.info("Feeds with no total entries (%d):", len(no_total_entries))
        for feed in no_total_entries:
            logger.info("  - %s (%s)", feed['title'], feed['url'])
    
    if no_recent_entries:
        logger.info("Feeds with no recent entries in past %d days (%d):", RECENT_DAYS, len(no_recent_entries))
        for feed in no_recent_entries:
            logger.info("  - %s (%d total entries) (%s)", feed['title'], feed['total_entries'], feed['url'])
else:
    logger.info("All feeds have recent entries")
       


def fix_broken_heading_elements(html_content):
    """
    Fix headings that got broken across multiple HTML elements.
    This handles cases where heading content got split, like:
    <h2>Text [ __](url-part-</h2><p>url-continued)</p>
    """
    # Pattern: heading with markdown link ending in dash, followed by paragraph with closing parenthesis
    # This specifically targets the issue we saw with Servo blog entries
    broken_heading_pattern = r'(<h[1-6][^>]*>)(.*?)\[[^\]]*\]\([^)]*-(</h[1-6]>)\s*<p>([^)]*\)[^<]*)</p>'
    
    def fix_broken_heading(match):
        opening_tag = match.group(1)   # <h2>
        heading_text = match.group(2)  # 'Highlights '
        closing_tag = match.group(3)   # </h2>
        # group(4) is the <p> content with the URL continuation - we ignore it
        
        # Clean up the heading text by removing any remaining HTML and extra whitespace
        clean_text = re.sub(r'<[^>]*>', '', heading_text).strip()
        clean_text = re.sub(r'\s+', ' ', clean_text)
        
        return f"{opening_tag}{clean_text}{closing_tag}"
    
    return re.sub(broken_heading_pattern, fix_broken_heading, html_content, flags=re.IGNORECASE | re.DOTALL)
