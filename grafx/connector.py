import requests
import json
from chilitools.grafx.auth import GraFxAuth
from chilitools.grafx.environment import GraFxEnvironment
from chilitools.grafx.api.environment import Templates
from chilitools.grafx.api.platform import Platform


#Todo(austin): Make some like exception handling thing where you just check_response(resp) and it throws for the usual 401 stuff, etc.

# Gonna embrace the class madness I guess.
class GraFxConnector:
    def __init__(self, environment: str, environment_type: str = "production", client_id: str = None, client_secret: str = None, logger = None, api_version: str = "1"):
        self.environment = environment
        self.auth = GraFxAuth(client_id, client_secret)
        self.environment = GraFxEnvironment(
            environment_name=environment,
            environment_type=environment_type,
            api_version=api_version
        )
        self.logger = logger
        self.templates = Templates(self)
        self.platform = Platform(self)

    def make_request(self, api: str, method: str, endpoint: str, headers: dict = None, query_params: dict = None, body: dict = None):

        if api == "platform":
            req_url = self.platform_base_url + endpoint
        else:
            req_url = self.environment.base_url + endpoint

        req_headers = {
            "content-type": "application/json",
            "Authorization": f"Bearer {self.auth.token}"
        }

        # If additional headers were supplied, merge them
        if headers: req_headers = req_headers | headers

        req_method = method.lower()

        if not body: body = {}
        if isinstance(body, dict): body = json.dumps(body)

        resp = requests.request(method=req_method,
                                url=req_url,
                                headers=req_headers,
                                params=query_params,
                                data=body)

        return resp




