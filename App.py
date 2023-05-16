from flask import Flask, redirect, request
from flask_cors import CORS
import pymongo
from config import MONGO_DATABASE, MONGO_URI
import random
import string
import re
regex = re.compile(
        # r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

print(re.match(regex, "http://www.example.com") is not None) # True
print(re.match(regex, "example.com") is not None) 
client = pymongo.MongoClient(
    MONGO_URI,
    connect=False,
)
db = client[MONGO_DATABASE]
app = Flask(__name__)
CORS(app)


client = pymongo.MongoClient(
    MONGO_URI,
    connect=False,
)
db = client[MONGO_DATABASE]

uiEndPoint = 'https://cutit-server.onrender.com/'


@app.route("/<hash>", methods=["GET"])
def geturl(hash):
    try:
        print(hash)
        if hash:
            urlres = db.urls.find_one({"hash": hash})
            if urlres:
                url = urlres["url"]
                if not url.startswith("http"):
                    url = "https://"+url
                return redirect(url, code=302)
            else:
                return redirect("/invalid_url/"+hash, code=302)
    except Exception as e:
        return {"response": {"error": str(e)}}


# write a function to generate a random alphanumeric string of length 6 using python3

def hash_generator():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))


@app.route("/", methods=["POST"])
def get_hash():
    try:
        jsonRequest =request.get_json(force=True)
        if jsonRequest["url"] and re.match(regex, jsonRequest["url"]) is not None:
            url = jsonRequest["url"]
            url = url.lower()
            urlres = db.urls.find_one({"url": url})
            if urlres:
                hash = urlres["hash"]
            else:
                hash = hash_generator()
                db.urls.insert_one({"url": url, "hash": hash})
            return {
                'short_url': uiEndPoint+hash
            }
        else:
            return "Invalid url", 400
    except Exception as e:
        return {"response": {"error": str(e)}}


if __name__ == "__main__":
    app.run(debug=True)
