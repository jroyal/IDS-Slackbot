__author__ = 'jhroyal'
import xmltodict
from lib.rtcworkitem import RTCWorkItem

def get_work_item(rtc, itemNumber):
        '''
        Get a work item's information

        Only captures the ID, Title, State, OwnedBy, and Type fields.
        :param itemNumber: The work item ID number
        :return: RTCWorkItem or None if there isn't one
        '''
        result = "*Finding information for work item %s*\n\n" % itemNumber
        url = "/rpt/repository/workitem?fields=workitem/workItem[id=%s]/" \
              "(summary|id|description|owner/name|state/name|projectArea/name|type/name)" % itemNumber

        response = rtc.get(url)
        output = xmltodict.parse(response.text)
        if "workItem" not in output["workitem"]:
            result += "I couldn't find any work items with the id %s." % itemNumber
        output = output["workitem"]["workItem"]
        workitem = RTCWorkItem(rtc.get_url(), output)

        result += "*<%s|%s %s: %s>*\n" \
                   "IDS Project: %s\n" \
                   "State: %s\n" \
                   "> Description: %s" % (workitem.url, workitem.type, workitem.id, workitem.summary,
                                        workitem.project, workitem.state, workitem.description)
        return result