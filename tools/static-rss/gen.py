# requires:
#  - feedparser==6
#  - html2text==2024.2.26
#  - markdown==3
#  - python-dateutil==2
#  - requests==2

import html
import logging
import datetime
import itertools
import multiprocessing.dummy
from typing import Iterator, Optional
from dataclasses import dataclass

import markdown
import requests
import html2text
import feedparser
import dateutil.parser


logger = logging.getLogger("gen")
logging.basicConfig(level=logging.DEBUG)


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


@dataclass
class Entry:
    timestamp: datetime.datetime
    title: str
    link: str
    content: str
    feed: Feed


def fetch_feed(feed: Feed) -> Iterator[Entry]:
    logger.debug("fetching feed: %s", feed.title)

    d = feedparser.parse(feed.url)

    for entry in d.entries:

        if feed.category == "rss" or feed.category == "release":
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
                timestamp=dateutil.parser.parse(entry.updated),
                title=entry.title,
                link=entry.link,
                content=content_html,
                feed=feed,
            )

        elif feed.category == "mastodon":
            # mastodon post RSS feed

            content_md = html2text.html2text(entry.summary)
            content_html = markdown.markdown(content_md)
            
            yield Entry(
                timestamp=dateutil.parser.parse(entry.updated),
                # use first line of content
                title=content_md.partition("\n")[0],
                link=entry.link,
                content=content_html,
                feed=feed,
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
    Feed(
         category="rss",
         title="Willi Ballenthin",
         url="http://www.williballenthin.com/index.xml", 
         homepage="http://www.williballenthin.com/"
    ),
    Feed(
         category="rss",
         title="Jessitron",
         url="http://blog.jessitron.com/feeds/posts/default", 
         homepage="https://jessitron.com"
    ),
    Feed(
         category="rss",
         title="Without boats, dreams dry up",
         url="https://without.boats/index.xml", 
         homepage="https://without.boats/"
    ),
    Feed(
         category="rss",
         title="Register Spill",
         url="https://registerspill.thorstenball.com/feed", 
         homepage="https://registerspill.thorstenball.com"
    ),
    Feed(
         category="rss",
         title="The Pragmatic Engineer",
         url="http://blog.pragmaticengineer.com/rss/", 
         homepage="https://blog.pragmaticengineer.com/"
    ),
    Feed(
         category="rss",
         title="Rust Blog",
         url="http://blog.rust-lang.org/feed.xml", 
         homepage="https://blog.rust-lang.org/"
    ),
    Feed(
         category="rss",
         title="Stories by nusenu on Medium",
         url="https://medium.com/feed/@nusenu", 
         homepage="https://medium.com/@nusenu?source=rss-d10fe243b17f------2"
    ),
    Feed(
         category="rss",
         title="Dan Luu",
         url="http://danluu.com/atom.xml", 
         homepage="https://danluu.com/atom/index.xml"
    ),
    Feed(
         category="rss",
         title="Ted Kaminski",
         url="http://www.tedinski.com/feed.xml", 
         homepage="http://www.tedinski.com/"
    ),
    Feed(
         category="rss",
         title="Zeus WPI",
         url="https://zeus.ugent.be/feed.xml", 
         homepage="https://zeus.ugent.be/"
    ),
    Feed(
         category="rss",
         title="Anton Zhiyanov",
         url="https://antonz.org/feed.xml", 
         homepage="https://antonz.org/"
    ),
    Feed(
         category="rss",
         title="SparkFun Tutorials",
         url="http://www.sparkfun.com/feeds/tutorials", 
         homepage="https://learn.sparkfun.com/tutorials"
    ),
    Feed(
         category="rss",
         title="the morning paper",
         url="http://blog.acolyer.org/feed/", 
         homepage="https://blog.acolyer.org"
    ),
    Feed(
         category="rss",
         title="Arne Bahlo",
         url="https://arne.me/feed.xml", 
         homepage="https://arne.me"
    ),
    Feed(
         category="rss",
         title="Andrew Ayer - Blog",
         url="https://www.agwa.name/blog/feed", 
         homepage="https://www.agwa.name/blog"
    ),
    Feed(
         category="rss",
         title="Emacs - Sacha Chua",
         url="http://sachachua.com/wp/category/emacs/feed/", 
         homepage="https://sachachua.com/blog/category/emacs"
    ),
    Feed(
         category="rss",
         title="g/ianguid/o.today",
         url="https://g7o.today/feed.xml", 
         homepage="https://g7o.today/"
    ),
    Feed(
         category="rss",
         title="Cal Paterson",
         url="http://calpaterson.com/calpaterson.rss", 
         homepage="https://calpaterson.com/calpaterson.rss"
    ),
    Feed(
         category="rss",
         title="Probably Dance",
         url="http://probablydance.com/feed/", 
         homepage="https://probablydance.com"
    ),
    Feed(
         category="rss",
         title="James Sinclair",
         url="http://jrsinclair.com/index.rss", 
         homepage="https://jrsinclair.com/"
    ),
    Feed(
         category="rss",
         title="Mr. Money Mustache",
         url="http://feeds.feedburner.com/MrMoneyMustache", 
         homepage="https://www.mrmoneymustache.com"
    ),
    Feed(
         category="rss",
         title="secret club",
         url="https://secret.club/feed.xml", 
         homepage="https://secret.club/"
    ),
    Feed(
         category="rss",
         title="Electric Fire Design",
         url="https://electricfiredesign.com/feed/", 
         homepage="https://electricfiredesign.com"
    ),
    Feed(
         category="rss",
         title="Stephen Diehl",
         url="http://www.stephendiehl.com/feed.rss", 
         homepage="http://www.stephendiehl.com"
    ),
    Feed(
         category="rss",
         title="Lambda the Ultimate",
         url="http://lambda-the-ultimate.org/rss.xml", 
         homepage="http://lambda-the-ultimate.org"
    ),
    Feed(
         category="rss",
         title="srcbeat",
         url="http://www.srcbeat.com/index.xml", 
         homepage="https://www.srcbeat.com/"
    ),
    Feed(
         category="rss",
         title="jank blog",
         url="https://jank-lang.org/blog/feed.xml", 
         homepage="https://jank-lang.org/blog/"
    ),
    Feed(
         category="rss",
         title="Andrew Healey's Blog",
         url="https://healeycodes.com/feed.xml", 
         homepage="https://healeycodes.com"
    ),
    Feed(
         category="rss",
         title="Kalzumeus Software",
         url="http://www.kalzumeus.com/feed/", 
         homepage="https://www.kalzumeus.com"
    ),
    Feed(
         category="rss",
         title="HPy",
         url="https://hpyproject.org/rss.xml", 
         homepage="https://hpyproject.org/"
    ),
    Feed(
         category="rss",
         title="seanmonstar",
         url="http://seanmonstar.com/rss", 
         homepage="https://seanmonstar.com/"
    ),
    Feed(
         category="rss",
         title="The Grumpy Economist",
         url="http://johnhcochrane.blogspot.com/feeds/posts/default", 
         homepage="https://johnhcochrane.blogspot.com/"
    ),
    Feed(
         category="rss",
         title="Cryptography &amp; Security Newsletter",
         url="https://www.feistyduck.com/bulletproof-tls-newsletter/feed", 
         homepage="https://www.feistyduck.com/newsletter/"
    ),
    Feed(
         category="rss",
         title="Paul Khuong: some Lisp",
         url="http://www.pvk.ca/atom.xml", 
         homepage="https://www.pvk.ca/"
    ),
    Feed(
         category="rss",
         title="Servo Blog",
         url="http://blog.servo.org/feed.xml", 
         homepage="https://servo.org"
    ),
    Feed(
         category="rss",
         title="Baby Steps",
         url="http://smallcultfollowing.com/babysteps/atom.xml", 
         homepage="https://smallcultfollowing.com/babysteps/"
    ),
    Feed(
         category="rss",
         title="Luke Muehlhauser",
         url="http://feeds.feedburner.com/LukeMuehlhauser", 
         homepage="https://lukemuehlhauser.com"
    ),
    Feed(
         category="rss",
         title="Locklin on science",
         url="http://scottlocklin.wordpress.com/feed/", 
         homepage="https://scottlocklin.wordpress.com"
    ),
    Feed(
         category="rss",
         title="matklad",
         url="https://matklad.github.io//feed.xml", 
         homepage="https://matklad.github.io"
    ),
    Feed(
         category="rss",
         title="tonsky.me",
         url="http://tonsky.me/blog/atom.xml", 
         homepage="https://tonsky.me/"
    ),
    Feed(
         category="rss",
         title="delan azabani",
         url="https://www.azabani.com/feed/tag/home.xml", 
         homepage="https://www.azabani.com/"
    ),
    Feed(
         category="rss",
         title="Fosskers.ca Blog",
         url="https://www.fosskers.ca/en/rss", 
         homepage="https://www.fosskers.ca"
    ),
    Feed(
         category="rss",
         title="sacha chua :: living an awesome life",
         url="http://feeds.feedburner.com/sachac", 
         homepage="https://sachachua.com"
    ),
    Feed(
         category="rss",
         title="Llogiq on stuff",
         url="http://llogiq.github.io/feed.xml", 
         homepage="https://llogiq.github.io/"
    ),
    Feed(
         category="rss",
         title="Articles by thoughtram",
         url="http://feeds.feedburner.com/thoughtram", 
         homepage="http://blog.thoughtram.io/"
    ),
    Feed(
         category="rss",
         title="Julia Evans",
         url="http://jvns.ca/atom.xml", 
         homepage="http://jvns.ca"
    ),
    Feed(
         category="rss",
         title="Stavros' Stuff Latest Posts",
         url="http://feeds.feedburner.com/stavrosstuff", 
         homepage="http://www.stavros.io/"
    ),
    Feed(
         category="rss",
         title="Drew DeVault's blog",
         url="https://drewdevault.com/feed.xml", 
         homepage="https://drewdevault.com"
    ),
    Feed(
         category="rss",
         title="Project Zero",
         url="http://googleprojectzero.blogspot.com/feeds/posts/default", 
         homepage="https://googleprojectzero.blogspot.com/"
    ),
    Feed(
         category="rss",
         title="Papers We Love",
         url="http://paperswelove.org/feed.xml", 
         homepage="http://papers-we-love.github.io/"
    ),
    Feed(
         category="rss",
         title="The Mad Ned Memo",
         url="https://madned.substack.com/feed/", 
         homepage="https://madned.substack.com"
    ),
    Feed(
         category="rss",
         title="News Minimalist",
         url="https://rss.beehiiv.com/feeds/4aF2pGVAEN.xml",
         homepage="https://newsletter.newsminimalist.com"
    ),
]

# take the 20 most recently updated repos
for repo in requests.get("https://api.github.com/users/williballenthin/starred?sort=updated&direction=desc&per_page=20").json():
    title = repo["full_name"]
    logger.debug("found repo: %s", title)

    homepage = f"https://github.com/{title}"
    url = homepage + "/releases.atom"
    feeds.append(
        Feed("release", url, homepage=homepage, title=title)
    )

with multiprocessing.dummy.Pool(16) as pool:
    entries = list(pool.imap_unordered(fetch_feed, feeds))
    entries = list(itertools.chain.from_iterable(entries))

# only show entries within the past three days
now = datetime.datetime.now()
three_days_ago = (now - datetime.timedelta(days=3)).date()
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
       
