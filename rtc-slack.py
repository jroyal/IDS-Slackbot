__author__ = 'jhroyal'

from rtcclient import RTCClient
import requests
import json
import yaml
import sqlite3
import time


def send_message_to_slack(url, channel, workitem):
    payload = {
        "channel": channel,
        "attachments": [
            {
                "fallback": "<%s|%s %s> has been updated!" % (workitem.url, workitem.type, workitem.id),
                "pretext": "A workitem has been updated!",
                "color": "good",
                "fields": [{
                               "title": "Update",
                               "value": "<%s|%s %s: %s> \nState has been changed to %s" % (
                               workitem.url, workitem.type, workitem.id, workitem.summary, workitem.state),
                               "short": False
                           }
                ]
            }
        ]
    }
    print "sending a message to slack"
    requests.post(url, data=json.dumps(payload))


def has_status_changed(workitem):
    workitem_has_changed = False
    conn = sqlite3.connect("rtcworkitem.db")
    db = conn.cursor()
    db.execute("CREATE TABLE IF NOT EXISTS workitems (id INTEGER PRIMARY KEY , state TEXT)")
    db.execute("SELECT * FROM workitems WHERE id=?", (workitem.id,))
    db_line = db.fetchone()
    if db_line:
        if db_line[1] != workitem.state:
            print "Workitem %s has changed." % workitem.id
            db.execute("UPDATE workitems SET state=? WHERE id=?", (workitem.state, workitem.id))
            workitem_has_changed = True
        else:
            workitem_has_changed = False
    else:
        print "Adding workitem %s to the db" % workitem.id
        db.execute("INSERT INTO workitems VALUES (?, ?)", (workitem.id, workitem.state))
        workitem_has_changed = True

    conn.commit()
    conn.close
    return workitem_has_changed


def run():
    env = yaml.load(file("env.yaml"))
    squad_list = []
    for squad in env["SQUAD_LIST"]:
        rtc = RTCClient(env["JAZZ_URL"],
                        env["JAZZ_USERNAME"],
                        env["JAZZ_PASSWORD"],
                        squad["squad"])
        squad_list.append((rtc, squad["channel"]))

    while True:
        for rtc, channel in squad_list:
            workitems = rtc.get_squad_workitems()
            for workitem in workitems:
                if has_status_changed(workitem):
                    send_message_to_slack(env["SLACK_URL"], channel, workitem)

        time.sleep(env["POLLING_INTERVAL"])


if __name__ == '__main__':
    run()