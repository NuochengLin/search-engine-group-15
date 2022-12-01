from flask import Flask, request, render_template
from flask_cors import CORS
from query import parse_query, search

app = Flask(__name__)
CORS(app, supports_credentials=True)

@app.route('/')
def index():
    return render_template('search_engine.html')


@app.route("/api")
def get_results():
    response = {
      "status": 0,
      "msg": "",
      "data": {
        "items": []
      }
    }

    if request.args.get("query") == None:
        return response

    terms = parse_query(request.args.get("query"))
    if not terms:
        response["status"] = -1
        response["msg"] = "Invalid query!"
        return response

    items, time = search(terms)
    response["data"]["items"] = items
    response["data"]["time"] = time

    return response

