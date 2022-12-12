import xmltodict
import json

from typing import OrderedDict
from requests import Response
from chilitools.utilities.defaults import statusCodes

class ChiliResponse:

    def __init__(self, response: Response):
        self.response = response
        self.statusCode = response.status_code
        self.success = False
        self.parseSuccess = False

        if 'content-type' in self.response.headers:
            self.type = self.response.headers['content-type'].split(';')[0]
        else:
            self.type = None

        if self.response.status_code in statusCodes:
            self.statusDescription = statusCodes[self.response.status_code]
            if self.response.status_code == 200 or self.response.status_code == 201:
                self.success = True
        else:
            self.statusDescription = f"Status code description not found for status code {self.response.status_code}"

        self._parseContent()

    def _parseContent(self):
        if self.type == 'application/xml':
            try:
                self.data = xmltodict.parse(self.text)
                self.parseSuccess = True
            except:
                self.data = { "error":"failed to parse xml" }
        elif self.type == 'application/json':
            try:
                self.data = self.response.json()
                self.parseSuccess = True
            except:
                self.data = { "error":"failed to parse json" }
        else:
            self.data = { "error":"failed to find a proper method to parse the response" }

    def asDict(self) -> dict:
        return {"success":self.success, "statusCode":self.response.status_code, "statusDescription":self.statusDescription, "data":self.data, "contentType":self.type, "responseText":self.response.text}

    def contentAsDict(self) -> dict:
        return self.data

    def didSucceed(self) -> bool:
        return self.success

    def getURL(self) -> str:
        if 'urlInfo' in self.data:
            return self.data['urlInfo']['@url']
        return "There is no URL node found in the result that can be processed"

    def __repr__(self) -> str:
         return f'ChiliResponse(success={self.success}, statusCode={self.response.status_code}, statusDescription={self.statusDescription}, data={self.data}, contentType={self.type}, responseText={self.response.text})'

    def __str__(self) -> str:
        return f'ChiliResponse(success={self.success}, statusCode={self.response.status_code}, statusDescription={self.statusDescription}, data={self.data}, contentType={self.type}, responseText={self.response.text})'

    def __iter__(self):
        yield from self.data

    @property
    def text(self) -> str:
        return self.response.text

    @property
    def content(self) -> OrderedDict:
        return self.contentAsDict()

    @property
    def json(self) -> str:
        return json.dumps(self.data)

    @property
    def status(self) -> dict:
        return {"code": self.response.status_code, "description":self.statusDescription}