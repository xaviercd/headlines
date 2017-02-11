from flask import Flask
from flask import render_template
from flask import request
from flask import make_response
import feedparser
import json
import urllib2
import urllib
import datetime


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


def get_value_with_fallback(key):
    if request.args.get(key):
        return request.args.get(key)
    elif request.cookies.get(key):
        return request.cookies.get(key)
    else:
        return DEFAULTS[key]


@app.route("/")
def home():
    publication = get_value_with_fallback('publication')
    articles = get_news(publication)

    city = get_value_with_fallback('city')
    weather = get_weather(city)

    currency_from = get_value_with_fallback('currency_from')
    currency_to = get_value_with_fallback("currency_to")

    rate, currencies = get_rate(currency_from, currency_to)

    response = make_response(render_template("home.html", articles=articles, weather=weather,
                           currency_from=currency_from, currency_to=currency_to, rate=rate,
                           currencies=sorted(currencies)))
    expires = datetime.datetime.now() + datetime.timedelta(seconds=30)
    response.set_cookie("publication", publication, expires=expires)
    response.set_cookie("city", city, expires=expires)
    response.set_cookie("currency_from", currency_from, expires=expires)
    response.set_cookie("currency_to", currency_to, expires=expires)
    return response


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
