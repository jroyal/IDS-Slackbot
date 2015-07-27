__author__ = 'jhroyal'

import requests
import json
import argparse
import os


class SlackCommandException(BaseException):
    pass


class SlackArgumentParser(argparse.ArgumentParser):
    def exit(self, status=0, message=None):
        if message:
            raise SlackCommandException(message)

    def _print_message(self, message, file=None):
        if message:
            raise SlackCommandException(message)

    def error(self, message):
        raise SlackCommandException(message)


def get_argument_parser():
    description = "Application that queries Track and Plan dashboards and sends results to slack."
    parser = SlackArgumentParser(description=description, prog='/ids')
    parser.add_argument("-n", default=5, help="Number of work items to retrieve. Default is 5.")
    parser.add_argument("-a", "--all", action="store_true", help="Returns all work items")
    parser.add_argument("first_name")
    parser.add_argument("last_name")
    return parser


def remove_resolved(work_items):
    finished_workitems = {'Resolved': True, 'Done': True, 'Invalid': True}
    result = []
    for work_item in work_items:
        if work_item.state not in finished_workitems:
            result.append(work_item)
    return result


def priority_to_val(work_item):
    conversion = {"High": 3,
                  "Medium": 2,
                  "Low": 1,
                  "Unassigned": 0}
    return conversion[work_item.priority]


def send_to_slack(args, slack_form, work_items):
    """
    Send the message to slack that alerts users that a poll has been created
    :param url: The url to send the poll too
    :param poll: The json that represents the poll
    :return: None
    """
    print args
    print slack_form
    payload = {
        "channel": slack_form["user_id"],
        "text": "Here are the work items for %s %s!" % (args.first_name, args.last_name),
        "link_names": 1,
        "attachments": [

        ]
    }
    filtered_workitems = remove_resolved(work_items)
    for index, work_item in enumerate(sorted(filtered_workitems, key=priority_to_val, reverse=True)):
        if index >= int(args.n):
            break
        WI = {
            "fallback": "Here are the work items for %s %s!" % (args.first_name, args.last_name),
            "title": "%s %s: %s" % (work_item.type, work_item.id, work_item.summary),
            "title_link": work_item.url,
            "mrkdwn_in": ["fields", "text"],
            "text": "*Project:* %s\n"
                    "*Priority:* %s\n"
                    "*State:* %s \n" % (work_item.project, work_item.priority, work_item.state)
        }
        payload["attachments"].append(WI)

    print "Sending an update to slack"
    requests.post(os.environ["slack_url"], data=json.dumps(payload))