__author__ = 'jhroyal'
import xmltodict
import requests
from lib.rtcworkitem import RTCWorkItem

def get_users_workitems(rtc, user):
    workitems = []
    result = "*The work items for %s*\n\n" % user
    url = "/rpt/repository/workitem?fields=workitem/workItem[owner/name='%s']/" \
          "(summary|id|description|owner/name|state/(name|group)|projectArea/name|type/name)" % user
    try:
        response = rtc.get(url)
    except requests.exceptions.ReadTimeout:
        return "Request timed out :("
    output = xmltodict.parse(response.text)
    if "workItem" not in output["workitem"]:
        result += "I couldn't find any work items for %s.\n" \
                  "If you think this is wrong, make sure that you have the users full name." % user
    else:
        output = output["workitem"]["workItem"]
        #print json.dumps(output, indent=4, sort_keys=True)
        if not isinstance(output, list):
            if output["state"]["group"] == "open":
                workitems.append(RTCWorkItem(rtc.get_url(), output))
        else:
            for workitem in output:
                if workitem["state"]["group"] == "open":
                    workitems.append(RTCWorkItem(rtc.get_url(), workitem))

        for workitem in workitems:
            result += "*<%s|%s %s: %s>*\n" \
                      "IDS Project: %s\n" \
                      "State: %s\n" \
                      "> Description: %s\n\n" % (workitem.url, workitem.type, workitem.id, workitem.summary,
                                                 workitem.project, workitem.state, workitem.description)
    return result