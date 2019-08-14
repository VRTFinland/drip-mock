import uuid

from flask import Flask, request, Response
from subscriber_mock_data import (
    subscriber_template
)

app = Flask(__name__)
DATA = {
    "events": [],
    "subscribers": {}
}

SUBSCRIBERS_COUNTER = 0
EVENTS_COUNTER = 0


@app.route("/v2/<account_id>", methods=["GET"])
def hello_world(account_id):
    return "Woot woot"


@app.route("/v2/<account_id>/subscribers", methods=["GET", "POST"])
def subscribers(account_id):
    if request.method == "GET":
        return {
            "links": {"subscribers.account": "https://api.getdrip.com/v2/accounts/{subscribers.account}"},
            "meta": {
                "page": 1,
                "count": len(DATA["subscribers"].keys()),
                "total_pages": 1,
                "total_count": len(DATA["subscribers"])
            },
            "subscribers": DATA["subscribers"]
        }

    elif request.method == "POST":
        data = request.json.get("subscribers", [])[0]
        subscriber = {}
        for key in subscriber_template.keys():
            subscriber[key] = data.get(key, subscriber_template[key])
        DATA["subscribers"][uuid.uuid4().hex] = subscriber

        return generate_post_response(subscriber)


@app.route("/v2/<account_id>/events", methods=["POST"])
def events(account_id):
    DATA["events"].append(request.json["events"][0])
    return Response(None, status=204)


@app.route("/v2/<account_id>/event_actions", methods=["GET"])
def event_actions(account_id):
    return {
        "meta": {
            "count": 2,
            "page": 1,
            "total_count": 2,
            "total_pages": 1
        },
        "event_actions": [event.get("action", "Unknown") for event in DATA["events"]]
    }


def generate_post_response(subscriber):
    return {
        "links": {"subscribers.account": "https://api.getdrip.com/v2/accounts/{subscribers.account}"},
        "subscribers": [subscriber]
    }


if __name__ == '__main__':
    app.run()
