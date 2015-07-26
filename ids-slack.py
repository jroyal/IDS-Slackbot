__author__ = 'jhroyal'

import os
import argparse
import utils

from pyIDS import IDS
from flask import Flask
from flask import request

app = Flask(__name__)

# TODO: Show usages
class ThrowingArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise Exception(message)

@app.route('/', methods=['GET', 'POST'])
def ids_cli():
    print request.form
    client = app.config["client"]
    if request.method == "GET":
        print client.get_work_item_by_id(16219).description
        return "IDS Service is running"

    parser = ThrowingArgumentParser(description='Argparse Test script')
    parser.add_argument("-n", "--name", nargs=2, help='FirstName LastName', required=True)

    try:
        args = parser.parse_args(request.form["text"].split(" "))
    except Exception as err:
        return str(err)

    owner = args.name[0] + " " + args.name[1]
    print owner
    work_items = client.get_work_items_by_owner(owner)
    print len(work_items)
    print work_items
    utils.send_to_slack(os.environ["slack_url"], request.form["user_id"], work_items)
    return "Getting your work items"

if __name__ == "__main__":
    if "user" not in os.environ:
        raise Exception("Please provide a username!")
    if "pass" not in os.environ:
        raise Exception("Please provide a password!")
    if "server" not in os.environ:
        raise Exception("Please provide a jazz server!")
    app.config["client"] = IDS("https://hub.jazz.net/"+os.environ["server"],
                               os.environ["user"],
                               os.environ["pass"])
    app.run(host="0.0.0.0", port=5000)
