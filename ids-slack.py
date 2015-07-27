__author__ = 'jhroyal'

import os
import argparse
import utils

from pyIDS import IDS
from flask import Flask
from flask import request

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def ids_cli():
    client = app.config["client"]
    if request.method == "GET":
        return "IDS Service is running!"

    try:
        parser = utils.get_argument_parser()
        args = parser.parse_args(request.form["text"].split(" "))
    except utils.SlackCommandException as err:
        return str(err)

    owner = args.first_name + " " + args.last_name
    work_items = client.get_work_items_by_owner(owner)
    if work_items is None:
        return "Unable to find any work items for %s" % owner
    utils.send_to_slack(args, request.form, work_items)
    return "Getting your work items"

if __name__ == "__main__":
    if "user" not in os.environ:
        raise Exception("Please provide a username!")
    if "pass" not in os.environ:
        raise Exception("Please provide a password!")
    if "server" not in os.environ:
        raise Exception("Please provide a jazz server!")
    if "slack_url" not in os.environ:
        raise Exception("Please provide an incoming webhook for your slack account!")
    app.config["client"] = IDS("https://hub.jazz.net/"+os.environ["server"],
                               os.environ["user"],
                               os.environ["pass"])
    app.run(host="0.0.0.0", port=5000)
