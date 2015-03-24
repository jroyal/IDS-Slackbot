__author__ = 'jhroyal'
import requests
import json
import xmltodict
import logging as log
from rtcworkitem import RTCWorkItem

class RTCClient(object):
    '''
    A class to encapsulate the work needed to send REST calls to the IBM Devops Service RTC backend.
    '''
    def __init__(self, url, user, password):
        log.info("Creating a RTCClient")
        self.base_url = url
        self.jazz_user = user
        self.jazz_pass = password

        self.session = requests.Session()
        self.session.verify = False
        self.session.allow_redirects = True
        self.session.headers = {'accept': 'application/json'}
        self.session.auth = (self.jazz_user, self.jazz_pass)

        log.debug("Request for authenticated resource")
        auth_uri = "/authenticated/identity"
        response = self.session.get(self.base_url + auth_uri, verify=False)

        if 'x-com-ibm-team-repository-web-auth-msg' in response.headers and response.headers['x-com-ibm-team-repository-web-auth-msg'] == 'authrequired':
            log.debug("Not currently authenticated")

            # Form response
            log.debug("Sending login POST")
            login_response = self.session.post(self.base_url + '/j_security_check',
                                               data={'j_username': self.jazz_user, 'j_password': self.jazz_pass})
            log.debug(login_response.headers)

            if 'x-com-ibm-team-repository-web-auth-msg' in login_response.headers and login_response.headers['x-com-ibm-team-repository-web-auth-msg'] == 'authrequired':
                log.error("Failed to authenticate")
                log.debug(login_response.status_code)
                log.debug(login_response.text)
                raise Exception("Failed to login: ", login_response.text)

            log.debug("Getting authenticated resource again now that we should be logged in:")
            response = self.session.get(self.base_url + auth_uri)
            log.debug(response.headers)
            log.debug(response.text)

    def get_url(self):
        return self.base_url

    def get(self, url):
        return self.session.get(self.base_url + url, verify=False, timeout=2.85)

    def get_work_item(self, itemNumber):
        '''
        Get a work item's information

        Only captures the ID, Title, State, OwnedBy, and Type fields.
        :param itemNumber: The work item ID number
        :return: RTCWorkItem or None if there isn't one
        '''
        log.info("Getting info on work item %s" % itemNumber)
        url = "/rpt/repository/workitem?fields=workitem/workItem[id=%s]/" \
              "(summary|id|description|owner/name|state/name|projectArea/name|type/name)" % itemNumber

        response = self.session.get(self.base_url + url, verify=False, timeout=2.85)
        output = xmltodict.parse(response.text)
        if "workItem" not in output["workitem"]:
            return None
        output = output["workitem"]["workItem"]
        print json.dumps(output, indent=4, sort_keys=True)
        return RTCWorkItem(self.base_url, output)


    def add_comment_to_workitem(self, itemNumber, comment):
        new_comment = {"dc:description": comment}
        self.session.headers["Content-Type"] = "application/x-oslc-cm-change-request+json"
        self.session.headers["accept"] = "text/json"
        url = "/oslc/workitems/%s/rtc_cm:comments" % itemNumber
        response = self.session.post(self.base_url + url, verify=False, timeout=2.85, data=json.dumps(new_comment))
        output = response.text
        print output
        print json.dumps(json.loads(output), indent=4, sort_keys=True)


    def get_squad_workitems(self, project):
        '''
        Get a projects work items. No filtering on them for now.

        Only captures the ID, Title, State, OwnedBy, and Type fields.
        :return: Array of RTCWorkItems
        '''
        log.info("Getting squad work items for project %s" % project)
        workitems = []

        url = "/rpt/repository/workitem?fields=workitem/workItem[projectArea/name='%s']/" \
              "(summary|id|description|owner/name|state/name|projectArea/name|type/name)" % project
        response = self.session.get(self.base_url + url, verify=False, timeout=2.85)
        output = xmltodict.parse(response.text)["workitem"]["workItem"]
        #print json.dumps(output, indent=4, sort_keys=True)
        for workitem in output:
            workitems.append(RTCWorkItem(self.base_url, workitem))
        return workitems

    def get_users_workitems(self, user):
        log.info("Getting the work items for %s" % user)
        workitems = []

        url = "/rpt/repository/workitem?fields=workitem/workItem[owner/name='%s']/" \
              "(summary|id|description|owner/name|state/(name|group)|projectArea/name|type/name)" % user
        response = self.session.get(self.base_url + url, verify=False, timeout=2.85)
        output = xmltodict.parse(response.text)
        if "workItem" not in output["workitem"]:
            return None
        output = output["workitem"]["workItem"]
        #print json.dumps(output, indent=4, sort_keys=True)
        if not isinstance(output, list):
            if output["state"]["group"] == "open":
                workitems.append(RTCWorkItem(self.base_url, output))
        else:
            for workitem in output:
                if workitem["state"]["group"] == "open":
                    workitems.append(RTCWorkItem(self.base_url, workitem))
        return workitems