from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from chilitools.grafx.connector import GraFxConnector

class Platform:
    def __init__(self, grafx_connector: GraFxConnector):
        self.connector = grafx_connector
        self.base_url = "https://api.chiligrafx.com/api/v1"

    def environment_info(self, id: str):
        return self.connector.make_request(
            api="platform",
            method="get",
            endpoint=f"/environments/{id}"
        )

