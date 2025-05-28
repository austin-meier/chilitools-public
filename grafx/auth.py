import requests
import datetime

from os import getenv


class GraFxAuth:
    def __init__(self, client_id: str = None, client_secret: str = None):
        # Check if credentials were supplied
        if all([client_id, client_secret]):
            self.client_id = client_id
            self.client_secret = client_secret
        elif getenv("GRAFX_EMAIL") and getenv("GRAFX_PASSWORD") and getenv("GRAFX_CLIENT_ID") and getenv("GRAFX_CLIENT_SECRET"):
            self.email = getenv("GRAFX_EMAIL")
            self.password = getenv("GRAFX_PASSWORD")
            self.client_id = getenv("GRAFX_CLIENT_ID")
            self.client_secret = getenv("GRAFX_CLIENT_SECRET")
        else:
            raise Exception("No valid credentials were found to use for GraFx Authentication please supply a `email`, `password`, `client_id`, and `client_secret` arguments to the GraFx Connector")


    @property
    def token(self):
        if hasattr(self, "_token") and not self._is_token_expired(self._token):
          return self._token["access_token"]

        headers = {
            "content-type": "application/json",
        }

        # User credentials password flow
        if hasattr(self, "email"):
            url = "https://login.chili-grafx.com/oauth/token"
            body = {
                "grant_type": "password",
                "audience": "https://chiligrafx.com",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "username": self.email,
                "password": self.password,
            }
        # Integration flow
        else:
            url = "https://integration-login.chiligrafx.com/oauth/token"
            body = {
                "grant_type": "client_credentials",
                "audience": "https://chiligrafx.com",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }

        resp = requests.post(
            url=url,
            headers=headers,
            json=body)

        if (resp.status_code != 200):
            raise Exception(f"There was an error generating the auth token\n{resp.text}")

        resp = resp.json()
        expiration_offset = int(resp['expires_in'] * .9)
        self._token = {
            "expiration_datetime": datetime.datetime.now() + datetime.timedelta(seconds=expiration_offset),
            "access_token": resp["access_token"]
        }
        return(resp["access_token"])

    def _is_token_expired(self, token):
        return datetime.datetime.now() > token["expiration_datetime"]
