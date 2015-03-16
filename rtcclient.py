__author__ = 'jhroyal'
import requests
import json
import xmltodict
import logging as log


class RTCWorkItem():
    '''
    Create an object to encapsulate all the info we are returning in a work item.
    '''
    def __init__(self, obj_json):
        log.debug("Creating a RTCWorkItem for %s" % obj_json["dc:identifier"])
        self.summary = obj_json["dc:title"]
        self.id = obj_json["dc:identifier"]
        self.description = obj_json["dc:description"]
        type_string = obj_json["dc:type"]["rdf:resource"]
        if "task" in type_string:
            self.type = "Task"
        elif "Story":
            self.type = "Story"
        self.state = self.get_state(obj_json["rtc_cm:state"]["rdf:resource"])
        self.url = obj_json["rdf:resource"]

    def get_state(self, url):
        '''
        Since RTC doesn't provide a human readable version of the state we need to translate them.
        states: idea = new, defined = in progress, tested=implemented, state.s2=invalid, verified=done

        :param url: The URL provided by RTC we parse to get the state
        :return The State in terms that match the UI
        '''
        value = "Unknown State"
        if "story" in url:
            if "idea" in url:
                value = "New"
            elif "defined" in url:
                value = "In Progress"
            elif "tested" in url:
                value = "Implemented"
            elif "verified" in url:
                value = "Done"
            elif "state.s2" in url:
                value = "Invalid"
            else:
                value = "Unknown State"
        elif "task" in url:
            state = url[url.rfind("/") + 1:]
            if state == "1":
                value = "New"
            elif state == "2":
                value = "In Progress"
            elif state == "3":
                value = "Done"

        return value

    def __str__(self):
        return """%s %s
    Summary: %s
    State: %s
        """ % (self.type, self.id, self.summary, self.state)


class RTCClient(object):
    '''
    A class to encapsulate the work needed to send REST calls to the IBM Devops Service RTC backend.
    '''
    def __init__(self, url, user, password, project):
        log.info("Creating a RTCClient for %s" % project)
        self.base_url = url
        self.jazz_user = user
        self.jazz_pass = password
        self.project = project
        self.project_uuid = None

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

    def _find_project_uuid(self):
        '''
        Find the unique project id used in RTC backend.
        :return: UUID of the objects project
        '''
        log.debug("Getting project uuid")
        uuid = None
        url = "/process/project-areas"
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        response = self.session.get(self.base_url + url, verify=False, headers=headers)
        projects = xmltodict.parse(response.text)["jp06:project-areas"]["jp06:project-area"]
        for project in projects:
            if self.project in project["@jp06:name"]:
                uuid = project["jp06:url"][project["jp06:url"].rfind("/") + 1:]
        return uuid

    def get_work_item(self, itemNumber):
        '''
        Get a work item's information

        Only captures the ID, Title, State, OwnedBy, and Type fields.
        :param itemNumber: The work item ID number
        :return: RTCWorkItem
        '''
        log.info("Getting info on work item %s" % itemNumber)
        url = "/oslc/workitems/%s.json?oslc_cm.properties=dc:identifier,dc:title,rtc_cm:state,rtc_cm:ownedBy,dc:type,dc:description" % itemNumber
        response = self.session.get(self.base_url + url, verify=False)
        # json.dumps(json.loads(response.text), indent=4, sort_keys=True)
        return RTCWorkItem(json.loads(response.text))

    def get_squad_workitems(self):
        '''
        Get a projects work items. No filtering on them for now.

        Only captures the ID, Title, State, OwnedBy, and Type fields.
        :return: Array of RTCWorkItems
        '''
        log.info("Getting squad work items for project %s" % self.project)
        workitems = []
        if self.project_uuid is None:
            self.project_uuid = self._find_project_uuid()
        url = "/oslc/contexts/%s/workitems.json?oslc_cm.properties=dc:identifier,dc:title,rtc_cm:state,rtc_cm:ownedBy,dc:type,dc:description" % self.project_uuid
        response = self.session.get(self.base_url + url, verify=False)
        unparsed_json = json.loads(response.text)
        # print json.dumps(json.loads(response.text), indent=4, sort_keys=True)
        for workitem in unparsed_json["oslc_cm:results"]:
            workitems.append(RTCWorkItem(workitem))
        log.debug("Found %s work items" % len(workitems))
        return workitems