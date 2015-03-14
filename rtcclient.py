__author__ = 'jhroyal'
import requests
import json
import xmltodict


class RTCClient(object):
    def __init__(self):
        self.base_url = "https://hub.jazz.net/ccm08"
        auth_uri = "/authenticated/identity"
        jazz_user = "username"
        jazz_pass = "password"

        self.session = requests.Session()
        self.session.verify = False
        self.session.allow_redirects = True
        self.session.headers = {'accept':'application/json'}
        self.session.auth = (jazz_user, jazz_pass)

        print "Request for authenticated resource"
        response = self.session.get(self.base_url + auth_uri, verify=False)

        print response.headers

        if 'x-com-ibm-team-repository-web-auth-msg' in response.headers and response.headers['x-com-ibm-team-repository-web-auth-msg'] == 'authrequired':
            print "Not currently authenticated"

            # Form response
            print "Sending login POST"
            login_response = self.session.post(self.base_url + '/j_security_check', data={ 'j_username': jazz_user, 'j_password': jazz_pass } )
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

    def getWorkItem(self, itemNumber):
        #original_url = "/rpt/repository/workitem?fields=workitem/workItem[id=%s]/(*)" % itemNumber
        old_url = "/oslc/workitems/%s.xml" %itemNumber
        response = self.session.get(self.base_url + old_url, verify=False)
        print response.headers
        print response.text
        output = xmltodict.parse(response.text)
        print json.dumps(output, indent=4, sort_keys=True)