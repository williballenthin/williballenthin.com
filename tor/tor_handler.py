import urllib2, datetime
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

class InstantaneousTorStatus(db.Model):
    date = db.DateTimeProperty(required=True)
    state = db.TextProperty(required=True)

def html_tag(tag, text):
    r = "<%s>" % (tag)
    for t in text:
        r += t
    r += "</%s>" % (tag)
    return r

def html(text):
    return html_tag("html", text)

def html_header(text):
    r = ""
    for t in text:
        r += t
    return html_tag("header", r + """<script type="text/javascript"> 
 
  var _gaq = _gaq || [];
  _gaq.push(['_setAccount', 'UA-23141359-1']);
  _gaq.push(['_trackPageview']);
 
  (function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
  })();
 
</script> 
    """)

def html_body(text):
    return html_tag("body", text)

def html_text(text):
    return text

class UpdateHandler(webapp.RequestHandler):
    def get(self):
        f = urllib2.urlopen("http://torstatus.blutmagie.de/ip_list_exit.php/Tor_ip_list_EXIT.csv")
        t = f.read()
        f.close()
        
        status = InstantaneousTorStatus(date=datetime.datetime.now(), state=t) 
        status.put()

        output = html([
                    html_header([]),
                    html_body([
                        html_text("update ok.")
                        ])
                    ])
        self.response.out.write(output)

class ListHandler(webapp.RequestHandler):
    def get(self):

        statuses = ""
        for status in InstantaneousTorStatus.gql("ORDER BY date DESC"):
            statuses += "<li><a href='./get/%s'>%s UTC</a></li>" % (status.key(), status.date)

        output = html([
                    html_header([]),
                    html_body([
                        html_tag("h1", [
                                html_text("Tor endpoints over time"),
                                ]),
                        html_tag("ul", [
                                statuses,
                                ])
                        ])
                    ])
        self.response.out.write(output)


class GetHandler(webapp.RequestHandler):
    def get(self, key):
        status = InstantaneousTorStatus.get(key)

        output = html([
                    html_header([]),
                    html_body([
                        html_tag("pre", [
                                html_text(status.state)
                                ])
                        ])
                    ])
        self.response.out.write(output)


def main():
  application = webapp.WSGIApplication([('/tor/status/update', UpdateHandler),
                                        ('/tor/status/get/(.*)', GetHandler),
                                        ('/tor/status/get/?', ListHandler)])
  run_wsgi_app(application)

if __name__ == '__main__':
    main()


