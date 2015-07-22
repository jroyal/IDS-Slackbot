__author__ = 'jhroyal'

import os

from pyIDS import IDS
from flask import Flask
from flask import request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def ids_cli():
    client = app.config["client"]
    if request.method == "GET":
        print client.get_work_item_by_id(16219).description
        return "IDS Service is running"

    print request.form["text"]
    return "Successfully called ids_cli"

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
