from flask import Flask
from flask import render_template
from flask import request
import feedparser
import json
import urllib2
import urllib

RSS_FEEDS = {
    "bbc": r"http://feeds.bbci.co.uk/news/rss.xml",
    "cnn": r"http://rss.cnn.com/rss/edition.rss",
    "iol": r"http://www.iol.co.za/cmlink/1.640",
    "fox": r"http://feeds.foxnews.com/foxnews/latest",
    "sina": r"http://rss.sina.com.cn/news/china/focus15.xml",
}

DEFAULTS = {
    'publication': "sina",
    'city': "Chengdu,China",
    'currency_from': 'USD',
    'currency_to': "CNY"
}

CURRENCY_URL = r"https://openexchangerates.org//api/latest.json?" \
               r"app_id=25e4e98c11254cd89789ac574e04cd07"
WEATHER_URL = r"http://api.openweathermap.org/data/2.5/weather?q={}&units=metric" \
              r"&appid=8f774df9c0bea2cea61f863ee7e53a88"

app = Flask(__name__)


@app.route("/")
def home():
    publication = request.args.get('publication')
    if not publication:
        publication = DEFAULTS['publication']
    articles = get_news(publication)

    city = request.args.get('city')
    if not city:
        city = DEFAULTS['city']
    weather = get_weather(city)

    currency_from = request.args.get("currency_from")
    if not currency_from:
        currency_from = DEFAULTS['currency_from']
    currency_to = request.args.get("currency_to")
    if not currency_to:
        currency_to = DEFAULTS['currency_to']

    rate, currencies = get_rate(currency_from, currency_to)

    return render_template("home.html", articles=articles, weather=weather,
                           currency_from=currency_from, currency_to=currency_to, rate=rate,
                           currencies=currencies)


def get_weather(query):
    query = urllib.quote(query)
    url = WEATHER_URL.format(query)
    data = urllib2.urlopen(url).read()
    parsed = json.loads(data)
    weather = None
    if parsed.get("weather"):
        weather = {
            "description": parsed["weather"][0]["description"],
            "temperature": parsed["main"]["temp"],
            "city": parsed["name"],
            "country": parsed['sys']['country']
        }

    return weather


def get_rate(frm, to):
    all_currency = urllib2.urlopen(CURRENCY_URL).read()

    parsed = json.loads(all_currency).get('rates')
    frm_rate = parsed.get(frm.upper())
    to_rate = parsed.get(to.upper())
    return to_rate/frm_rate, sorted(parsed.keys())


def get_news(query):
    if not query or query.lower() not in RSS_FEEDS:
        publication = DEFAULTS['publication']
    else:
        publication = query.lower()
    feed = feedparser.parse(RSS_FEEDS[publication])
    return feed["entries"]

if __name__ == "__main__":
    app.run(port=5000, debug=True)
