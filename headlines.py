from flask import Flask
import feedparser

RSS_FEEDS = {
    "bbc": r"http://feeds.bbci.co.uk/news/rss.xml",
    "cnn": r"http://rss.cnn.com/rss/edition.rss",
    "iol": r"http://www.iol.co.za/cmlink/1.640",
    "fox": r"http://feeds.foxnews.com/foxnews/latest",
    "sina": r"http://rss.sina.com.cn/sports/global/focus.xml",
}


app = Flask(__name__)


@app.route("/")
@app.route("/<publication>")
def get_news(publication="bbc", encoding="utf8"):
    feed = feedparser.parse(RSS_FEEDS[publication])
    first_article = feed["entries"][0]
    title = first_article.get("title", "").encode(encoding)
    published = first_article.get("published", "").encode(encoding)
    summary = first_article.get("summary", "").encode(encoding)
    return """<html>
        <body>
            <h1> {0} Headlines </h1>
            <b>{1}</b> <br/>
            <i>{2}</i> <br/>
            <p>{3}</p> <br/>
        </body>
    </html>""".format(publication.upper(), title, published, summary)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
