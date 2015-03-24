__author__ = 'jhroyal'
import xmltodict
import requests
from lib.rtcworkitem import RTCWorkItem

def retrieve_backlog(rtc, project):
    print "PROJECT: %s" % project
    workitems = []
    result = "*The backlog for %s*\n\n" % project
    url = "/rpt/repository/workitem?fields=workitem/workItem[projectArea/name='%s' and target/id='backlog']/" \
          "(summary|id|description|owner/name|state/(name|group)|projectArea/name|type/name|stringComplexity)" % project
    try:
        response = rtc.get(url)
    except requests.exceptions.ReadTimeout:
        return "Request timed out :("
    output = xmltodict.parse(response.text)
    if "workItem" not in output["workitem"]:
        result += "No items in the backlog!\n" \
                 "If you think this is wrong, make sure that you have the correct team name. " \
                 "Try /rtc help for more information."

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
                      "%s owns this %s workitem\n\n"  \
                      % (workitem.url, workitem.type, workitem.id, workitem.summary,
                         workitem.owner, workitem.state)
    return result
