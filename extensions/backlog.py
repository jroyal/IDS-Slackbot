__author__ = 'jhroyal'
import xmltodict
import re
import requests
from lib.rtcworkitem import RTCWorkItem


def retrieve_backlog(rtc, project):
    success, output = _find_full_project_name(rtc, project)
    if not success:
        return output
    else:
        project = output
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


def _find_full_project_name(rtc, requested_project):
    '''
    Find the project name if you know the project uuid.
    :return: Project Name
    '''
    match_projects = []
    for project in rtc.projects:
        if requested_project.lower() in project.lower():
            match_projects.append(project)
    if len(match_projects) > 1:
        return False, "Too many projects found with %s. Project name needs to be more specific." % requested_project
    elif len(match_projects) == 1:
        return True, match_projects[0]
    else:
        return False, "No projects found that match %s." % requested_project