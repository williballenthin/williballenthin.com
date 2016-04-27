import sys
import os
import urllib2
import datetime


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
    return html_tag("head", r + """<script type="text/javascript"> 
 
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

def main():
    f = urllib2.urlopen("http://torstatus.blutmagie.de/ip_list_exit.php/Tor_ip_list_EXIT.csv")
    t = f.read()
    f.close()
    
    d = datetime.datetime.utcnow().isoformat(" ") + " UTC"

    output = html([
                    html_header([]),
                    html_body([
                        html_tag("pre", [
                            t
                        ])
                    ])
                 ])
    with open(os.path.join(sys.argv[1], d + ".html"), "wb") as f:
        f.write(output)

if __name__ == "__main__":
    main()
