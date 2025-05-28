from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from chilitools.grafx.connector import GraFxConnector

from chilitools.grafx.document import GraFxDocument

class Templates:
    def __init__(self, grafx_connector: GraFxConnector):
        self.connector = grafx_connector

    def info(self, id: str):
        return self.connector.make_request(
            api="environment",
            method="get",
            endpoint=f"/templates/{id}"
        )

    def get(self, id: str):
        # Get the template metadata
        resp = self.info(id)
        if resp.status_code != 200:
            raise Exception(f"There was an issue getting the template metadata: {resp.text}")
        content = resp.json()
        doc_name = content["data"]["name"]
        doc_id = content["data"]["id"]

        # Get the template JSON
        resp = self.download(id)
        if resp.status_code != 200:
            raise Exception(f"There was an issue getting the template json: {resp.text}")

        doc_json = resp.text
        return GraFxDocument(doc=doc_json, id=doc_id, name=doc_name)

    def download(self, id: str):
        return self.connector.make_request(
            api="environment",
            method="get",
            endpoint=f"/templates/{id}/download"
        )

    def add(self, name: str, path: str = "/", json: str = None):
        return self.connector.make_request(
            api="environment",
            method="post",
            endpoint="/templates",
            query_params={"name": name, "folderPath": path},
            body=json
        )