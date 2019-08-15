import uuid
import os
from urllib.parse import urljoin

from flask import Flask, request, Response
from subscriber_mock_data import (
    subscriber_template
)

app = Flask(__name__)
DATA = {
    "events": [],
    "subscribers": {}
}
SUBSCRIBER_EMAIL_ID_MAP = {}

BASE_URL = os.environ.get("BASE_URL", "http://0.0.0.0:5000")


def reset_data():
    DATA.events = []
    DATA.subscribers = {}
    for key in SUBSCRIBER_EMAIL_ID_MAP:
        del SUBSCRIBER_EMAIL_ID_MAP[key]


@app.route("/reset", methods=["POST"])
def reset():
    reset_data()


@app.route("/v2/<account_id>", methods=["GET"])
def hello_world(account_id):
    return "Woot woot"


@app.route("/v2/<account_id>/subscribers/<subscriber_id>/", methods=["GET"])
def subscriber_handler(account_id, subscriber_id):
    if subscriber_id in DATA["subscribers"]:
        return DATA["subscribers"][subscriber_id]

    return None


@app.route("/v2/<account_id>/subscribers", methods=["GET", "POST"])
def subscribers_handler(account_id):
    if request.method == "GET":
        return {
            "links": {"subscribers.account": urljoin(BASE_URL, "/v2/accounts/{subscribers.account}")},
            "meta": {
                "page": 1,
                "count": len(DATA["subscribers"].keys()),
                "total_pages": 1,
                "total_count": len(DATA["subscribers"])
            },
            "subscribers": [subscriber for subscriber in DATA["subscribers"].values()]
        }

    elif request.method == "POST":
        data = request.json.get("subscribers", [])[0]
        email = data.get("email")
        subscriber_id = SUBSCRIBER_EMAIL_ID_MAP.get(email)

        if subscriber_id:
            subscriber = DATA["subscribers"][subscriber_id]
            for key in subscriber_template.keys():
                subscriber[key] = data.get(key, subscriber.get(key, subscriber_template.get(key)))
        else:
            subscriber_id = uuid.uuid4().hex
            subscriber = {}
            for key in subscriber_template.keys():
                subscriber[key] = data.get(key, subscriber_template[key])
            subscriber["id"] = subscriber_id
            subscriber["href"] = urljoin(BASE_URL, f"v2/{account_id}/subscribers/{subscriber_id}")
            DATA["subscribers"][subscriber_id] = subscriber
            SUBSCRIBER_EMAIL_ID_MAP[subscriber.get("email")] = subscriber_id

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
