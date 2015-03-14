__author__ = 'jhroyal'
import requests
import json
import xmltodict


class RTCWorkItem():
    def __init__(self, obj_json):
        self.summary = obj_json["dc:title"]
        self.id = obj_json["dc:identifier"]
        type_string = obj_json["dc:type"]["rdf:resource"]
        self.type = type_string[type_string.rfind("/") + 1:].title()
        self.state = self.get_state(obj_json["rtc_cm:state"]["rdf:resource"])
        self.url = obj_json["rdf:resource"]

    def get_state(self, url):
        # states: idea = new, defined = in progress, tested=implemented, state.s2=invalid, verified=done
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
    def __init__(self, env):
        self.base_url = env["JAZZ_URL"]
        self.jazz_user = env["JAZZ_USERNAME"]
        self.jazz_pass = env["JAZZ_PASSWORD"]
        self.project = env["PROJECT"]
        self.project_uuid = None
        auth_uri = "/authenticated/identity"
        self.session = requests.Session()
        self.session.verify = False
        self.session.allow_redirects = True
        self.session.headers = {'accept': 'application/json'}
        self.session.auth = (self.jazz_user, self.jazz_pass)

        print "Request for authenticated resource"
        response = self.session.get(self.base_url + auth_uri, verify=False)

        print response.headers

        if 'x-com-ibm-team-repository-web-auth-msg' in response.headers and response.headers['x-com-ibm-team-repository-web-auth-msg'] == 'authrequired':
            print "Not currently authenticated"

            # Form response
            print "Sending login POST"
            login_response = self.session.post(self.base_url + '/j_security_check',
                                               data={'j_username': self.jazz_user, 'j_password': self.jazz_pass})
            print login_response.headers

            if 'x-com-ibm-team-repository-web-auth-msg' in login_response.headers and login_response.headers['x-com-ibm-team-repository-web-auth-msg'] == 'authrequired':
                print "Failed to authenticate"
                print login_response.status_code
                print login_response.text
                raise Exception( "Failed to login: ", login_response.text )

            print "Getting authenticated resource again now that we should be logged in:"
            response = self.session.get(self.base_url + auth_uri )
            print response.headers
            print response.text

    def _find_project_uuid(self):
        uuid = None
        url = "/process/project-areas"
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        response = self.session.get(self.base_url + url, verify=False, headers=headers)
        projects = xmltodict.parse(response.text)["jp06:project-areas"]["jp06:project-area"]
        for project in projects:
            if self.project in project["@jp06:name"]:
                uuid = project["jp06:url"][project["jp06:url"].rfind("/") + 1:]
                print uuid
        return uuid


    def get_work_item(self, itemNumber):
        url = "/oslc/workitems/%s.json?oslc_cm.properties=dc:identifier,dc:title,rtc_cm:state,rtc_cm:ownedBy,dc:type" % itemNumber
        response = self.session.get(self.base_url + url, verify=False)
        print response.headers
        print json.dumps(json.loads(response.text), indent=4, sort_keys=True)
        return RTCWorkItem(json.loads(response.text))


    def get_filtered_results(self):
        if self.project_uuid is None:
            self.project_uuid = self._find_project_uuid()
        url = "/oslc/contexts/%s/workitems.json?oslc_cm.properties=dc:identifier,dc:title,rtc_cm:state,rtc_cm:ownedBy,dc:type" % self.project_uuid
        response = self.session.get(self.base_url + url, verify=False)
        print response.headers
        print json.dumps(json.loads(response.text), indent=4, sort_keys=True)