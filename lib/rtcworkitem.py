__author__ = 'jhroyal'


class RTCWorkItem():
    '''
    Create an object to encapsulate all the info we are returning in a work item.
    '''
    def __init__(self, url, obj):
        self.id = obj["id"]
        self.summary = obj["summary"]
        self.description = obj["description"]
        self.project = obj["projectArea"]["name"]
        self.url = "%s/resource/itemName/com.ibm.team.workitem.WorkItem/%s" % (url, obj["id"])
        self.state = obj["state"]["name"]
        self.type = obj["type"]["name"]
        self.owner = obj["owner"]["name"]

        if "stringComplexity" in obj:
            self.points = obj["stringComplexity"]

        if self.description:
            # Make the description a block quote in slack
            self.description = self.description.replace("\n", "\n>")
        else:
            self.description = "No description."

    def __str__(self):
        return """%s %s
    Summary: %s
    State: %s
        """ % (self.type, self.id, self.summary, self.state)