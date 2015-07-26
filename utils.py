__author__ = 'jhroyal'

import requests
import json

def send_to_slack(url, user_id, work_items):
    """
    Send the message to slack that alerts users that a poll has been created
    :param url: The url to send the poll too
    :param poll: The json that represents the poll
    :return: None
    """
    payload = {
        "channel": user_id,
        "text": "Your workitems!",
        "link_names": 1,
        "attachments": [
            {
                "fallback": "Your workitems!",
                "mrkdwn_in": ["fields", "text"],
                "fields": []
            }
        ]
    }
    for work_item in work_items:
        WI = {
            "title": "%s: %s" % (work_item.id, work_item.summary),
            "value": "%s" % (work_item.url)
        }
        payload["attachments"][0]["fields"].append(WI)

    print "Sending an update to slack"
    requests.post(url, data=json.dumps(payload))