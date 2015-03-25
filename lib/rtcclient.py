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

        self.projects = self.pre_load_projects()
        print "RTCClient created"


    def get_url(self):
        return self.base_url

    def get(self, url):
        return self.session.get(self.base_url + url, verify=False, timeout=2.85)

    def pre_load_projects(self):
        print "Preloading projects"
        url = "/process/project-areas"
        output = []
        response = self.get(url)
        projects = xmltodict.parse(response.text)["jp06:project-areas"]["jp06:project-area"]
        for project in projects:
            output.append(project["@jp06:name"])
        return output

    def add_comment_to_workitem(self, itemNumber, comment):
        new_comment = {"dc:description": comment}
        self.session.headers["Content-Type"] = "application/x-oslc-cm-change-request+json"
        self.session.headers["accept"] = "text/json"
        url = "/oslc/workitems/%s/rtc_cm:comments" % itemNumber
        response = self.session.post(self.base_url + url, verify=False, timeout=2.85, data=json.dumps(new_comment))
        output = response.text
        print output
        print json.dumps(json.loads(output), indent=4, sort_keys=True)

