from flask import Flask
from flask import render_template
from flask import request
import feedparser

RSS_FEEDS = {
    "bbc": r"http://feeds.bbci.co.uk/news/rss.xml",
    "cnn": r"http://rss.cnn.com/rss/edition.rss",
    "iol": r"http://www.iol.co.za/cmlink/1.640",
    "fox": r"http://feeds.foxnews.com/foxnews/latest",
    "sina": r"http://rss.sina.com.cn/news/china/focus15.xml",
}


app = Flask(__name__)


@app.route("/")
def get_news():
    query = request.args.get("publication")
    if not query or query.lower() not in RSS_FEEDS:
        publication = "bbc"
    else:
        publication = query.lower()
    feed = feedparser.parse(RSS_FEEDS[publication])
    return render_template("home.html", articles=feed["entries"])

if __name__ == "__main__":
    app.run(port=5000, debug=True)
