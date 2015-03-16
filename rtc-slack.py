__author__ = 'jhroyal'

from rtcclient import RTCClient
import requests
import json
import yaml
import sqlite3
import time
import logging as log
import sys, os
from flask import Flask
from flask import request
from multiprocessing import Process


app = Flask(__name__)


@app.route('/', methods=['POST'])
def rtc_command():
    requested_id = request.form["text"]
    token = request.form["token"]
    if os.getenv("SLACK_TOKEN") != token:
        return "Invalid slack token."

    rtc = RTCClient(os.getenv('JAZZ_URL'),
                    os.getenv('JAZZ_USERNAME'),
                    os.getenv('JAZZ_PASSWORD'),
                    os.getenv('PROJECT'))
    workitem = rtc.get_work_item(requested_id)
    return "*<%s|Workitem %s: %s>*\nState: %s\nDescription: %s" % (workitem.url, workitem.id, workitem.summary, workitem.state, workitem.description)

def send_message_to_slack(url, channel, workitems):
    '''
    Send a message to the specified slack url and channel.
    :param url: The URL given to you by the incoming WebHook in Slack
    :param channel: The channel you want to post in
    :param workitem: The RTCWorkItem Object that contains the information we are sending out
    :return: None
    '''
    payload = {
        "channel": channel,
        "text": "Some new work item updates!",
        "attachments": [
        ]
    }
    for workitem in workitems:
        state = workitem.state
        if state == "New":
            color = "#000000"
        elif state == "In Progress":
            color = "A0D8F1"  # blue
        elif state == "Implemented":
            color = "good"
        elif state == "Done":
            color = "good"
        elif state == "Invalid":
            color = "danger"
        else:
            color = "warning"
        payload["attachments"].append({
            "fallback": "<%s|%s %s> has been updated!" % (workitem.url, workitem.type, workitem.id),
            "color": color,
            "fields": [{
                           "value": "<%s|%s %s: %s> \nState has been changed to %s" % (workitem.url, workitem.type,
                                                                                       workitem.id, workitem.summary,
                                                                                       workitem.state),
                           "short": False
                       }
            ]
        })
    log.info("Sending an update to slack")
    requests.post(url, data=json.dumps(payload))


def has_status_changed(workitem):
    '''
    Update the DB with the status given by the work item.
    :param workitem: RTCWorkItem we are checking
    :return: True if work item is new or status has changed. False otherwise.
    '''
    workitem_has_changed = False
    conn = sqlite3.connect("rtcworkitem.db")
    db = conn.cursor()
    db.execute("CREATE TABLE IF NOT EXISTS workitems (id INTEGER PRIMARY KEY , state TEXT)")
    db.execute("SELECT * FROM workitems WHERE id=?", (workitem.id,))
    db_line = db.fetchone()
    if db_line:
        if db_line[1] != workitem.state:
            log.info("Workitem %s has changed." % workitem.id)
            db.execute("UPDATE workitems SET state=? WHERE id=?", (workitem.state, workitem.id))
            workitem_has_changed = True
        else:
            workitem_has_changed = False
    else:
        log.info("Adding workitem %s to the db" % workitem.id)
        db.execute("INSERT INTO workitems VALUES (?, ?)", (workitem.id, workitem.state))
        workitem_has_changed = True

    conn.commit()
    conn.close
    return workitem_has_changed


def run():
    '''
    Main method used in this program. Creates a series of RTCClients to talk to the respective projects. Sends a
    message to Slack if a work item has an updated status.
    :return: None
    '''
    log.info("Starting to run")
    squad_list = []
    # for squad in env["SQUAD_LIST"]:
    rtc = RTCClient(os.getenv('JAZZ_URL'),
                    os.getenv('JAZZ_USERNAME'),
                    os.getenv('JAZZ_PASSWORD'),
                    os.getenv('PROJECT'))
    squad_list.append((rtc, os.getenv("SLACK_CHANNEL")))

    first_time_through = True
    while True:
        log.info("Grabbing all work items for our projects.")
        for rtc, channel in squad_list:
            slack_outbound = []
            workitems = rtc.get_squad_workitems()
            for workitem in workitems:
                if has_status_changed(workitem):
                    slack_outbound.append(workitem)
            if len(slack_outbound) > 0 and not first_time_through:
                send_message_to_slack(os.getenv("SLACK_URL"), channel, slack_outbound)
        first_time_through = False
        time.sleep(float(os.getenv("POLLING_INTERVAL")))


port = os.getenv('VCAP_APP_PORT', '5000')
if __name__ == "__main__":
    log.basicConfig(filename='rtc-slack.log', level=log.DEBUG, format='%(asctime)s %(levelname)s:%(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S')
    p = Process(target=run)
    p.start()
    app.run(host='0.0.0.0', port=int(port))