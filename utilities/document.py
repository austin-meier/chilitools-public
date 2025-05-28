from lxml import etree

class ChiliDocument:
  def __init__(self, doc_xml: str):
    try:
      self.doc: etree._Element = etree.fromstring(doc_xml)
    except Exception as e:
      self.doc = None
      print(f"There was an error creating a Document from the XML\n {e}")

  @property
  def name(self):
    if self.doc is None: return
    return self.doc.attrib.get('name')

  @property
  def id(self):
    if self.doc is None: return
    return self.doc.attrib.get('id')

  def __str__(self) -> str:
    return self.to_xml()

  def to_xml(self) -> str:
    return etree.tostring(self.doc, method="xml", encoding="unicode")

  @property
  def datasource_id(self):
    if self.doc is None: return
    ds = self.get_datasource()
    if ds is not None: return ds.get('dataSourceID')
    return None

  def get_datasource(self):
    return self.doc.find("dataSource")

  def get_datasource_string(self) -> str:
    return etree.tostring(self.get_datasource(), encoding="unicode")

  def set_datasource(self, new_datasource):
    self.doc.replace(self.doc.find("dataSource"), new_datasource)

  def get_fonts(self):
    if self.doc is None: return
    fonts = []

    for font in self.doc.findall("fonts//"):
      fonts.append({
        "resource_type": "Fonts",
        "id": font.get("id"),
        "name": font.get("name"),
        "family": font.get("family"),
        "style": font.get("style")
      })

    return fonts

  def _get_frames(self, frame_type: str = "any"):
    if self.doc is None: return
    frames = []

    for frame in self.doc.findall("pages//frames/item"):
      inline_frames = frame.findall("inlineFrames//item//frame")
      if inline_frames:
        for e in inline_frames:
          if frame_type == "any" or e.get("type") == frame_type:
            frames.append(e)
      if frame_type == "any" or frame.get("type") == frame_type:
        frames.append(frame)
    return frames

  @property
  def frames(self):
    return self._get_frames(frame_type="any")

  def get_images(self):
    if self.doc is None: return
    images = []

    for image_frame in self._get_frames("image"):
      if image_frame.get("hasContent", "false") == "true":
        if len(image_frame.get("dynamicAssetProviderID", "")) > 1:
          images.append({
            "resource_type": "DynamicAssetProviders",
            "id": image_frame.get("dynamicAssetProviderID")
          })
        else:
          images.append({
            "resource_type": "Assets",
            "id": image_frame.get("externalID"),
            "name": image_frame.get("externalName", ""),
            "path": image_frame.get("path", "")
          })

    return images

  def get_barcode_ids(self):
    return [b.get("barcodeTypeID") for b in self.barcode_frames()]

  def barcode_frames(self):
    return self._get_frames(frame_type="barcode")

  def text_frames(self):
    return self._get_frames(frame_type="text")
