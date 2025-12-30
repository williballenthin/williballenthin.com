# /// script
# dependencies = ["feedparser"]
# ///
import feedparser
import sys
import logging

# Configure logging to stderr so it doesn't interfere with stdout
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("get-pinboard-urls")

RSS_URL = 'https://feeds.pinboard.in/rss/u:williballenthin/'

try:
    logger.info(f"Fetching RSS feed from {RSS_URL}")
    d = feedparser.parse(RSS_URL)

    if d.bozo:
        logger.warning(f"Feed parsing error: {d.bozo_exception}")

    urls = []
    for entry in d.entries[:10]:
        urls.append(entry.link)

    logger.info(f"Found {len(urls)} URLs")
    print("\n".join(urls))

except Exception as e:
    logger.error(f"Error fetching/parsing feed: {e}")
    sys.exit(1)
