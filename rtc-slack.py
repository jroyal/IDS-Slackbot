__author__ = 'jhroyal'

import json
import re
import logging as log
import sys
import os
import traceback

import requests
import yaml
from flask import Flask
from flask import request

from lib.rtcclient import RTCClient
from extensions.backlog import retrieve_backlog
from extensions.user import get_users_workitems

app = Flask(__name__)
env = dict()

@app.route('/', methods=['GET', 'POST'])
def rtc_command():
    if request.method == "GET":
        return "RTC Command is running and waiting for requests"
    requested = request.form["text"]
    user = request.form["user_name"]
    token = request.form["token"]
    if env["SLACK_TOKEN"] != token:
        return "Invalid slack token."
    rtc = env["RTC"]
    try:
        if re.match('^[0-9]+$', requested):
            workitem = rtc.get_work_item(requested)
            output = "*Finding information for work item %s*\n\n" % requested
            if workitem == None:
                return output + "I couldn't find any work items with the id %s." % requested

            return "*<%s|%s %s: %s>*\n" \
                   "IDS Project: %s\n" \
                   "State: %s\n" \
                   "> Description: %s" % (workitem.url, workitem.type, workitem.id, workitem.summary,
                                        workitem.project, workitem.state, workitem.description)

        elif "user" in requested:
            user = requested.replace("user", "").strip()
            return get_users_workitems(rtc, user)

        elif "backlog" in requested:
            project = requested.replace("backlog", "").strip()
            return retrieve_backlog(rtc, project)

        else:
            help_message = "*RTC-SLACKBOT help*\n\n" \
                           "`/rtc [id]` -- `/rtc 40034` -- Get information on a specific work item \n" \
                           "`/rtc user [name]` -- `/rtc user James Royal` -- Get a users open work items\n" \
                           "`/rtc backlog [team]` -- `/rtc backlog alchemy | Alchemy-OS-Innovation-A` -- Get a teams backlog"
            if "help" in requested:
                return help_message
            else:
                return "*Unknown command!* \n\n" + help_message
    except requests.exceptions.ReadTimeout:
        return "Request timed out :("
    except Exception as e:
        log.error(traceback.format_exc())
        if "SLACK_ERROR_URL" in env and "SLACK_ERROR_CHANNEL" in env:
            send_message_to_admin(env["SLACK_ERROR_URL"], env["SLACK_ERROR_CHANNEL"], user, requested, traceback.format_exc())
        return "Oh no! Something went wrong!"


def send_message_to_admin(url, channel, user, call, stacktrace):
    payload = {
        "channel": channel,
        "text": "There was an ERROR!!",
        "attachments": [
            {
                "fallback": "There was an error; check the log",
                "color": "danger",
                "fields": [
                    {
                        "title": "Here is some more information",
                        "value": "User: %s\n"
                                 "Command: %s\n"
                                 "%s" % (user, call, stacktrace),
                        "short": False
                    }
                ]
            }
        ]
    }
    log.info("Sending an update to slack")
    requests.post(url, data=json.dumps(payload))

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
            env["SLACK_TOKEN"] = os.getenv("SLACK_TOKEN")
            env["SLACK_ERROR_URL"] = os.getenv("SLACK_ERROR_URL")
            env["SLACK_ERROR_CHANNEL"] = os.getenv("SLACK_ERROR_CHANNEL")
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
