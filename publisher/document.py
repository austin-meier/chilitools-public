from lxml import etree

class DocumentFont:
  def __init__(self, id, name, family, style):
    self.id = id
    self.name = name,
    self.family = family
    self.style = style

class ChiliDocument:
  def __init__(self, doc_xml: str):
    try:
      self.doc: etree._Element = etree.fromstring(doc_xml)
    except Exception as e:
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
  def datasource(self):
    return self.doc.find("dataSource")

  def get_datasource_string(self) -> str:
    return etree.tostring(self.get_datasource(), encoding="unicode")

  def set_datasource(self, new_datasource):
    if isinstance(new_datasource, str):
      new_datasource = etree.fromstring()
    self.doc.replace(self.doc.find("dataSource"), new_datasource)

  @property
  def fonts(self):
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

  @property
  def images(self):
    if self.doc is None: return
    images = []

    for image_frame in self.doc.findall("pages//item[@type='image']"):
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

  def text_frames(self):
    return self.doc.findall("pages//item[@type='text']")

