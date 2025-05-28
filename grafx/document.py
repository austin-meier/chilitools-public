import json

class DocumentFont:
    def __init__(self, id: str, name: str, family: str, style: str):
        self.id = id
        self.name = name
        self.family = family
        self.style = style

class DocumentImage:
    def __init__(self, id: str):
        self.id = id;

class GraFxDocument:
    def __init__(self, doc: str, id: str = None, name: str = None):
        try:
            # We were passed a parsed JSON document
            if isinstance(doc, dict):
                self.doc = doc
            # We were passed the raw JSON string of the document
            if isinstance(doc, str):
                self.doc = json.loads(doc)
        except Exception as e:
            self.doc = {}
            print(f"FAILURE PARSING GRAFX DOCUMENT: {e}")

        if id: self.id = id
        if name: self.name = name

    @property
    def json(self): return str(self)

    @property
    def images(self):
      image_frames = []
      for page in self.doc["pages"]:
          for frame in page["frames"]:
                print(frame)
                if frame.get("frameType") == "image" or frame.get("type") == "image":
                    # Image is coming from a connector
                    if frame["src"].get("connectorId") or frame["src"].get("id") == "grafx-media":
                        image_id = frame["src"]["assetId"]
                    # Image is is a variable
                    if frame["src"].get("variableId") or frame["src"].get("type") == "variable":
                        var_id = frame["src"].get("variableId") or frame["src"].get("id")
                        # Find and get the asset Id from the variable
                        for var in self.doc["variables"]:
                            if var.get("id") == var_id:
                                image_id = var["src"]["assetId"]
                                break
                    image = DocumentImage(image_id)
                    image_frames.append(image)
      return image_frames

    @property
    def fonts(self):
        fonts = []
        for font in self.doc["stylekit"]["fonts"]:
            #TODO(austin) Fix this when they break me
            fonts.append(DocumentFont(font["fontId"], font["name"], font["fontFamily"], font["fontStyle"]))
        return fonts


    def __str__(self): return json.dumps(self.doc)
    def __repr__(self): return self.doc