__author__ = 'jhroyal'

import re
import logging as log
import sys
import os
import yaml
from flask import Flask
from flask import request

from lib.rtcclient import RTCClient
from extensions.backlog import retrieve_backlog
from extensions.user import get_users_workitems
from extensions.singleworkitem import get_work_item

app = Flask(__name__)
env = dict()

@app.route('/workitem', methods=['GET', 'POST'])
def rtc_workitem():
    if request.method == "GET":
        return "RTC Workitem Command is running and waiting for requests"
    if not valid_token(request.form["token"]):
        return "Invalid token! Please verify that you have the correct tokens setup."
    item_number = request.form["text"]

    if re.match('^[0-9]+$', item_number):
        return get_work_item(env["RTC"], item_number)
    else:
        help_message = "*rtc-workitem help*\n\n" \
                       "`/rtc [id]` -- `/rtc 40034` -- Get information on a specific work item \n"
        if "help" in item_number:
            return help_message
        else:
            return "*Invalid command!* \n\n" + help_message

@app.route('/user', methods=['GET', 'POST'])
def user_lookup():
    if request.method == "GET":
        return "RTC user lookup is running and waiting for requests"
    if not valid_token(request.form["token"]):
        return "Invalid token! Please verify that you have the correct tokens setup."
    user = request.form["text"]
    return get_users_workitems(env["RTC"], user)

@app.route('/backlog', methods=['GET', 'POST'])
def backlog_lookup():
    if request.method == "GET":
        return "RTC backlog lookup is running and waiting for requests"
    if not valid_token(request.form["token"]):
        return "Invalid token! Please verify that you have the correct tokens setup."
    team = request.form["text"]
    return retrieve_backlog(env["RTC"], team)


def valid_token(token):
    for stashed_token in env["SLACK_TOKENS"]:
        if token == stashed_token:
            return True
    return False

if __name__ == "__main__":
    log.basicConfig(filename='rtc-slack.log', level=log.DEBUG, format='%(asctime)s %(levelname)s:%(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S')
    global env
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "local":
            log.info("Try loading from a local env.yaml file")
            env = yaml.load(file("env.yaml"))
            env["HOST"] = 'localhost'
            env["PORT"] = 5000
        else:
            log.info("Loading environment variables from Bluemix")
            env["JAZZ_URL"] = os.getenv('JAZZ_URL')
            env["JAZZ_USERNAME"] = os.getenv('JAZZ_USERNAME')
            env["JAZZ_PASSWORD"] = os.getenv('JAZZ_PASSWORD')
            env["SLACK_ERROR_URL"] = os.getenv("SLACK_ERROR_URL")
            env["SLACK_ERROR_CHANNEL"] = os.getenv("SLACK_ERROR_CHANNEL")
            if os.getenv("WORKITEM_TOKEN"):
                env["SLACK_TOKENS"].append(os.getenv("WORKITEM_TOKEN"))
            if os.getenv("BACKLOG_TOKEN"):
                env["SLACK_TOKENS"].append(os.getenv("BACKLOG_TOKEN"))
            if os.getenv("USER_TOKEN"):
                env["SLACK_TOKENS"].append(os.getenv("USER_TOKEN"))
            env["HOST"] = '0.0.0.0'
            env["PORT"] = os.getenv('VCAP_APP_PORT', '5000')

        env["RTC"] = RTCClient(env['JAZZ_URL'],
                               env['JAZZ_USERNAME'],
                               env['JAZZ_PASSWORD'])
    except Exception as e:
        log.error("Failed to load the environment \n %s" % e)
        sys.exit(2)
    print env
    app.run(host=env["HOST"], port=env["PORT"])
