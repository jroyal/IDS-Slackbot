__author__ = 'jhroyal'

from rtcclient import RTCClient
import requests
import json
import yaml


def send_message_to_slack(url, workitem):
    payload = {
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
    requests.post(url, data=json.dumps(payload))


def load_env(self):
    pass


def test(env):
    rtc = RTCClient(env)
    workitem = rtc.get_work_item(43746)
    send_message_to_slack(env["SLACK_URL"], workitem)


def test2(env):
    rtc = RTCClient(env)
    rtc.get_filtered_results()

if __name__ == '__main__':
    env = yaml.load(file("env.yaml"))
    test2(env)