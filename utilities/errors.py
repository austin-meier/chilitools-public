class ErrorHandler:
    def __init__(self):
         self.errors = {
            "FILENOTFOUND":"File not found",
            "GENAPIKEY":"There was an issue generating an API key, please make sure your login credentials are correct",
            "GENLOGINFORURL":"TODO",
            "GENOAUTH":"There was an error generating an OAuth token using the credentials files. Please ensure your username and password are correct.",
            "INVALIDBACKOFFICEURL": "The CHILI BackOffice URL entered can not be proceessed, please try again. The URL should end with interface.aspx",
            "TASKNOTSUCCEEDED": "The task did not succeed"
        }

    def getError(self, errorName):
        if errorName in self.errors:
            return "ERROR: " + self.errors[errorName]
        else:
            return "ERROR: Somebody really messed up because the Error Name wasn't even found"