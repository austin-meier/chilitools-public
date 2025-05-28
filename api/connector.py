import requests
from datetime import datetime
from logging import Logger

from chilitools.api import endpoints
from chilitools.api.response import ChiliResponse
from chilitools.utilities.backoffice import getBaseURL, getRequestURL, getEnvironmentName
from chilitools.utilities.file import checkForFile, writeFile, readFile
from chilitools.settings.config import APIKEY_FILE


class ChiliConnector:
    def __init__(self, backofficeURL: str, logger = None, forceKeyRegen: bool = False, username: str = None, password: str = None, apiVersion: str = '1.2', debugLevel = 1):
        self.backofficeURL = backofficeURL
        # Yes I misspelled environment early on and haven't search replaced it yet :D
        self.environment = getEnvironmentName(backofficeURL=backofficeURL)
        self.baseURL = getBaseURL(backofficeURL=backofficeURL)
        self.apiVersion = apiVersion
        self.requestURL = getRequestURL(backofficeURL=backofficeURL, version=apiVersion)

        # Login information if present
        #TODO Refactor this so you get the credentials from the credentials file here and not at the generation level
        self.username = username
        self.password = password

        # Session
        self.session = requests.Session()

        # Reuse API keys or force new API key every call
        self.forceKeyRegen = forceKeyRegen

        # Set the logger if provided
        self.logger: Logger | None = logger

        # Set the debug level
        self.debugLevel = debugLevel

        # Endpoints
        self.resources = endpoints.Resources(self)
        self.system = endpoints.System(self)
        self.documents = endpoints.Documents(self)

    def makeRequest(self, method: str, endpoint: str, headers: dict = None, queryParams: dict = None, json: dict = None, authRequired: bool = True) -> ChiliResponse:

        requestURL = self.requestURL + endpoint

        requestHeaders = { "accept":"*/*" }

        # Get API key if Auth is required
        if authRequired:
            apiKey = self.getAPIKey()
            requestHeaders['API-KEY'] = apiKey

        if headers is not None:
            for header, value in headers.items():
                requestHeaders[header] = value

        requestQueryParams = {}

        if queryParams is not None:
            for param, value in queryParams.items():
                requestQueryParams[param] = value

        method = method.lower()

        resp = self.session.request(method=method, url=requestURL, headers=requestHeaders, params=requestQueryParams, json=json)

        response = ChiliResponse(resp)

        if self.debugLevel == 2:
            request = {'url':requestURL, 'method':method, 'headers':requestHeaders, 'queryParams':requestQueryParams, 'body':json}
            self._displayMsg({'request':request, 'response':response.text})

        return response

    # This is a nightmare of a function. Don't ever do this again Austin
    def getAPIKey(self) -> str:
        genKey = True

        if self.debugLevel == 2:
            if self.username and self.password:
                self._displayMsg("ChiliConnector: Using supplied credentials instead of stored credentials to authenticate")

        if self.forceKeyRegen:
            self._displayMsg("ChiliConnector: Forcing a new API key to be generated")
        else:
            if checkForFile(APIKEY_FILE):
                try:
                    apiKeys = readFile(fileName=APIKEY_FILE, isJSON=True)
                except:
                    apiKeys = {}
            else:
                self._displayMsg("ChiliConnector: Key file not found, creating one...")
                apiKeys = {}

            if self.backofficeURL in apiKeys:
                if datetime.now() < datetime.fromisoformat(apiKeys[self.backofficeURL]['validTill']):
                    return apiKeys[self.backofficeURL]['key']
                else:
                    self._displayMsg(f"ChiliConnector: Key found for {self.backofficeURL} is expired, generating a new one...")
            else:
                self._displayMsg(f"ChiliConnector: Key not found for {self.backofficeURL}, generating one...")

        if genKey:
            keyResp = self.system.GenerateApiKey(username=self.username, password=self.password)
            if not keyResp.success:
                # This should only happen if the request is malformed or the user cannot connect to the environment API
                self._displayMsg("ChiliConnector: There was an issue connecting to the environment. Please try again or contact support", error=True)
                print(keyResp)
                exit(0)
            key = keyResp.content['apiKey']

            while key["@succeeded"] == "false":
                self._displayMsg(keyResp)
                self._displayMsg("ChiliConnector: There was an issue authenticating with CHILI. Please check the error message below", error=True)
                self._displayMsg(f"Error: {key['@errorMessage']}\n", error=True)

                if self.username and self.password:
                    print("Please enter your CHILI username")
                    username = input().strip()
                    print("Please enter your CHILI password")
                    password = input().strip()
                else:
                    from chilitools.api.mycp import deleteLoginFile, inputCredentials
                    deleteLoginFile()
                    print("Enter your login information again, or press CTRL-C to exit")
                    inputCredentials()
                keyResp = self.system.GenerateApiKey(username=self.username, password=self.password)
                key = keyResp.content['apiKey']


            if "@key" in key.keys():
                # Don't store the key if they are forceRegen
                if self.forceKeyRegen: return key["@key"]

                # Date format checking
                validTill = key['@validTill'].replace(' ', 'T').replace('Z', '')
                apiKeys[self.backofficeURL] = {'key':key['@key'], 'validTill':validTill}
                self._displayMsg(f"ChiliConnector: Successfully generated API key for {self.backofficeURL}")
            else:
                self._displayMsg(f"ChiliConnector: Error extracting API key from response: {key}", error=True)

        # Save key file
        writeFile(fileName=APIKEY_FILE, data=apiKeys, isJSON=True)
        return apiKeys[self.backofficeURL]['key']

    # honestly not sure the best way to pass log level without bigger refactor.
    def _displayMsg(self, msg: str, error: bool = False):
        if self.logger:
            if error:
                self.logger.error(msg)
            else:
                self.logger.info(msg)
        else:
            print(msg)

    def __repr__(self) -> str:
        return self.asDict()

    def __str__(self) -> str:
        return f'ChiliConnector(backofficeURL={self.backofficeURL}, environment={self.environment}, baseURL={self.baseURL}, requestURL={self.requestURL})'

    def asDict(self) -> dict:
        return {"backofficeURL":self.backofficeURL, "environment":self.environment, "baseURL":self.baseURL, "requestURL":self.requestURL}

