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


def check_if_positive(value):
    """
    Check if the provided argument value is a positive integer
    :param value: The value for -n passed to the argparser
    :return: the value if valid
    """
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("%s is not a positive integer!" %
                                         value)
    return ivalue


def get_argument_parser():
    description = "Application that queries Track and Plan dashboards and " \
                  "sends results to slack."
    parser = SlackArgumentParser(description=description, prog='/ids')
    parser.add_argument("-n", default=5, type=check_if_positive,
                        help="Number of work items to retrieve. Default is 5.")
    parser.add_argument("-a", "--all", action="store_true",
                        help="Returns all work items")
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


def post_to_slack(text, attachments=[]):
    """
    :param text: Plain text to send in the message
    :param attachments: JSON-encoded array of attachments.
                        https://api.slack.com/docs/attachments
    :return: result of the post
    """
    if not text:
        raise Exception("The 'text' argument cannot be None or empty")
    payload = {
        "channel": os.environ["slack_user_id"],
        "text": str(text),
        "link_names": 1,
        "attachments": attachments
    }
    print "Posting message to Slack"
    return requests.post(os.environ["slack_url"], data=json.dumps(payload))


def send_workitems_to_slack(args, work_items):
    """
    Send the message to slack that alerts users that a poll has been created
    :param args: The command-line arguments provided by the user
    :param work_items: The list of work items owned by the user provided
    :return: None
    """
    print args
    slack_attachments = []
    filtered_workitems = remove_resolved(work_items)
    for index, work_item in enumerate(sorted(filtered_workitems, key=priority_to_val, reverse=True)):
        WI = {
            "fallback": "Here are the work items for %s %s!" % (args.first_name, args.last_name),
            "title": "%s %s: %s" % (work_item.type, work_item.id, work_item.summary),
            "title_link": work_item.url,
            "mrkdwn_in": ["fields", "text"],
            "text": "*Project:* %s\n"
                    "*Priority:* %s\n"
                    "*State:* %s \n" % (work_item.project, work_item.priority, work_item.state)
        }
        slack_attachments.append(WI)
        if index >= int(args.n) - 1 and not args.all:
            break

    slack_text = "Showing %d out of %d work items for *%s %s*!" % \
                 (index + 1, len(filtered_workitems), args.first_name,
                  args.last_name)
    print "Sending work items to slack"
    post_to_slack(slack_text, slack_attachments)
