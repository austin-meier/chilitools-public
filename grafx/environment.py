class GraFxEnvironment:
    def __init__(self, environment_name: str, environment_type: str, api_version: str):
        self.name = environment_name
        self.type = environment_type
        self.version = api_version

    @property
    def base_url(self):
        return f"https://{self.name}.{self._get_host()}.online/grafx/api/v{self.version}/environment/{self.name}"


    @property
    def publisher_url(self):
        return f"https://{self.name}.{self._get_host()}.online/{self.name}/interface.aspx"

    def _get_host(self):
        if self.type == "sandbox":
            return "chili-publish-sandbox"
        else:
            return "chili-publish"