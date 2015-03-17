__author__ = 'jhroyal'

from rtcclient import RTCClient
import json
import re
import yaml
import logging as log
import sys
import os
from flask import Flask
from flask import request



app = Flask(__name__)
env = dict()

@app.route('/', methods=['GET', 'POST'])
def rtc_command():
    if request.method == "GET":
        return "RTC Command is running and waiting for requests"
    requested = request.form["text"]
    token = request.form["token"]
    if env["SLACK_TOKEN"] != token:
        return "Invalid slack token."
    rtc = env["RTC"]
    if re.match('^[0-9]+$', requested):
        workitem = rtc.get_work_item(requested)

        return "*<%s|%s %s: %s>*\n" \
               "IDS Project: %s\n" \
               "State: %s\n" \
               "> Description: %s" % (workitem.url, workitem.type, workitem.id, workitem.summary,
                                    workitem.project, workitem.state, workitem.description)
    else:
        workitems = rtc.get_users_workitems(requested)
        if workitems == None:
            return "No workitems found."
        output = ""
        for workitem in workitems:
            if workitem.description:
                description = workitem.description.replace("\n", "\n>")
            else:
                description = "No description."
            output += "*<%s|%s %s: %s>*\n" \
               "IDS Project: %s\n" \
               "State: %s\n" \
               "> Description: %s\n\n" % (workitem.url, workitem.type, workitem.id, workitem.summary,
                                    workitem.project, workitem.state, description)
        return output




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
