import uuid
import os
from urllib.parse import urljoin

from flask import Flask, request, Response
from subscriber_mock_data import (
    subscriber_template
)

app = Flask(__name__)


class DripData:
    def __init__(self):
        self.events = []
        self.tags = []
        self.subscribers = {}
        self.email_id_map = {}

    def reset_data(self):
        self.events = []
        self.tags = []
        self.subscribers = {}
        self.email_id_map = {}


dripData = DripData()

BASE_URL = os.environ.get("BASE_URL", "http://0.0.0.0:5000")


@app.route("/reset", methods=["POST"])
def reset():
    dripData.reset_data()
    return Response(None, status=204)


@app.route("/v2/<account_id>", methods=["GET"])
def hello_world(account_id):
    return "Woot woot"


@app.route("/v2/<account_id>/subscribers/<subscriber_id>", methods=["GET"])
def subscriber_handler(account_id, subscriber_id):
    subscriber = dripData.subscribers[subscriber_id]
    if subscriber is not None:
        return {
            "links": {"subscribers.account": urljoin(BASE_URL, "/v2/accounts/{subscribers.account}")},
            "meta": {
                "page": 1,
                "count": 1,
                "total_pages": 1,
                "total_count": 1
            },
            "subscribers": [subscriber]
        }
    return None


@app.route("/v2/<account_id>/subscribers", methods=["GET", "POST"])
def subscribers_handler(account_id):
    if request.method == "GET":
        return {
            "links": {"subscribers.account": urljoin(BASE_URL, "/v2/accounts/{subscribers.account}")},
            "meta": {
                "page": 1,
                "count": len(dripData.subscribers.keys()),
                "total_pages": 1,
                "total_count": len(dripData.subscribers)
            },
            "subscribers": [subscriber for subscriber in dripData.subscribers.values()]
        }

    elif request.method == "POST":
        data = request.json.get("subscribers", [])[0]
        email = data.get("email")
        subscriber_id = dripData.email_id_map.get(email)

        if subscriber_id:
            subscriber = dripData.subscribers[subscriber_id]
            for key in subscriber_template.keys():
                subscriber[key] = data.get(key, subscriber.get(key, subscriber_template.get(key)))
        else:
            subscriber_id = uuid.uuid4().hex
            subscriber = {}
            for key in subscriber_template.keys():
                subscriber[key] = data.get(key, subscriber_template[key])
            subscriber["id"] = subscriber_id
            subscriber["href"] = urljoin(BASE_URL, f"v2/{account_id}/subscribers/{subscriber_id}")
            dripData.subscribers[subscriber_id] = subscriber
            dripData.email_id_map[email] = subscriber_id

        return generate_post_response(subscriber)


@app.route("/v2/<account_id>/events", methods=["POST"])
def events(account_id):
    dripData.events.append(request.json["events"][0])
    return Response(None, status=204)

@app.route("/v2/<account_id>/tags", methods=["GET", "POST"])
def tags(account_id):
    if request.method == "GET":
        return {
            "tags" : dripData.tags
        }
    elif request.method == "POST":
        data = request.json.get("tags", [])[0]
        email = data.get("email")
        new_tag = data.get("tag")
        subscriber_id = dripData.email_id_map.get(email)
        if subscriber_id:
            subscriber = dripData.subscribers[subscriber_id]
            subscriber_tags = subscriber["tags"]
            if new_tag not in subscriber_tags:
                subscriber_tags.append(new_tag)
            if new_tag not in dripData.tags:
                dripData.tags.append(new_tag)
        return Response(response={}, status=201)

@app.route("/v2/<account_id>/subscribers/<email>/tags/<tag_name>", methods=["DELETE"])
def delete_tag(account_id, email, tag_name):
    subscriber_id = dripData.email_id_map.get(email)
    if subscriber_id:
        subscriber = dripData.subscribers[subscriber_id]
        subscriber_tags = subscriber["tags"]
        if tag_name in subscriber_tags:
            subscriber_tags.remove(tag_name)
    return Response(None, status=204)

@app.route("/v2/<account_id>/event_actions", methods=["GET"])
def event_actions(account_id):
    actions = [event.get("action") for event in dripData.events]

    return {
        "meta": {
            "count": len(actions),
            "page": 1,
            "total_count": len(actions),
            "total_pages": 1
        },
        "event_actions": actions
    }


def generate_post_response(subscriber):
    return {
        "links": {"subscribers.account": "https://api.getdrip.com/v2/accounts/{subscribers.account}"},
        "subscribers": [subscriber]
    }


if __name__ == '__main__':
    app.run()
