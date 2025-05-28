import base64
from time import sleep
from chilitools.api.connector import ChiliConnector
from chilitools.utilities.file import writeFile, readFile, checkForFile
from chilitools.utilities.logger import getLogger
from chilitools.utilities.document import ChiliDocument


class ServerMigrator:
  def __init__(self, srcChili: ChiliConnector, destChili: ChiliConnector, directory: str, verbose: bool = False, update: bool = False):
    # Try to load the progress JSON file
    self.progressFile = directory+'/progress.json'
    if checkForFile(fileName=self.progressFile):
      print("Found progress file for server migration, loading it.")
      self.progress = readFile(fileName=self.progressFile, isJSON=True)
      if self.progress.get('sourceUsername'):
        print("Loading user information for source environment")
        self.source = ChiliConnector(backofficeURL=self.progress['sourceURL'], username=self.progress['sourceUsername'], password=self.progress['sourcePassword'])
      else:
        self.source = ChiliConnector(backofficeURL=self.progress['sourceURL'])

      if self.progress.get('destUsername'):
        print("Loading user information for destination environment")
        self.dest = ChiliConnector(backofficeURL=self.progress['destURL'], username=self.progress['destUsername'], password=self.progress['destPassword'])
      else:
        self.dest = ChiliConnector(backofficeURL=self.progress['destURL'])
    else:
      # progress JSON not found
      self.source = srcChili
      self.dest = destChili
      self.progress = {'sourceURL': srcChili.backofficeURL, 'destURL': destChili.backofficeURL, 'resources':{}}
      if self.source.username:
        self.progress['sourceUsername'] = self.source.username
        self.progress['sourcePassword'] = self.source.password
      if self.dest.username:
        self.progress['destUsername'] = self.dest.username
        self.progress['destPassword'] = self.dest.password
      self._saveProgressFile()

    self.directory = directory
    self.logger = getLogger(directory+'/ServerMigrator.log')
    self.verbose = verbose
    self.interval = 1
    self.update = update

  def getResourceTrees(self):
    self.logger.info("Getting list of resource items")
    resources = set()
    r = self.source.resources.getResourceList().content
    for item in r['resources']['item']: resources.add(item['@name'].lower())
    for resource in resources:
      if not resource in self.progress['resources'].keys() or self.update:
        self.getResourceTree(resource)
      elif self.verbose: print(f"Already found resource tree for {resource}. Pass the update=True arg to force update the tree")

  def getResourceTree(self, resource: str, parentFolder: str = ''):
    resource = resource.lower()
    self.logger.info(f"Getting resource tree for {resource}.. This may take some time depending on size")
    resp = self.source.resources.ResourceGetTreeLevel(resourceType=resource, parentFolder=parentFolder, numLevels=-1, includeSubDirectories=True)
    if resp.success:
      path = f"{self.directory}/{resource}/{resource}.json"
      writeFile(fileName=path, data=resp.content, isJSON=True)
      self.progress['resources'][resource] = {'treeFile': path}
      self._saveProgressFile()
    else:
      self.logger.error(resp.asDict())

  def transferAll(self):
    for resource in self.progress['resources'].keys():
      self.transferResource(resource)

  def transferList(self, resource: str, itemList: str):
    resource = resource.lower()

    if resource not in self.progress['resources'].keys():
      self.progress['resources'][resource] = {'toTransfer':[]}

    # Check if there are items still in the transfer queue from a previous transfer
    if 'toTransfer' in self.progress['resources'][resource].keys() and len(self.progress['resources'][resource]['toTransfer']) > 0:
      self.logger.info(f'Found {resource} still queued to be transferred from previously')
      self.__transferItems(resource)
    else:
      for item in itemList:
        if self.verbose:
          self.logger.info(f"Getting item definition XML for ID: {item}")
        resp = self.source.resources.ResourceItemGetDefinitionXML(
          resourceType=resource,
          itemID=item
        )
        if not resp.success:
          if resource == "fonts":
            self.logger.warn(f"There was an issue getting item definition for {resource} with id: {item}")
          else:
            self.logger.error(f"There was an issue getting item definition for {resource} with id: {item}")
          if self.verbose:
            print(resp.asDict())
        else:
          itemXML = resp.contentAsDict()['item']
          itemXML['@path'] = itemXML['@relativePath']
          self.progress['resources'][resource]['toTransfer'].append(itemXML)
          #self._saveProgressFile()
      self.__transferItems(resource=resource, disablePreviews=False)

  def transferResource(self, resource: str, parentFolder: str = '', customPath: str = None):
    resource = resource.lower()
    if not resource in self.progress['resources'].keys() or self.update or 'treeFile' not in self.progress['resources'][resource].keys():
      self.logger.info(f'Updating {resource} directory tree structure')
      self.getResourceTree(resource, parentFolder)

    # Check if there are items still in the transfer queue from a previous transfer
    if 'toTransfer' in self.progress['resources'][resource].keys() and len(self.progress['resources'][resource]['toTransfer']) > 0:
      self.logger.info(f'Found {resource} still queued to be transferred from previously')
      self.__transferItems(resource)
    else:
      self.progress['resources'][resource]['toTransfer'] = []
      filePath = self.progress['resources'][resource]['treeFile']
      if checkForFile(fileName=filePath):
        items = readFile(self.progress['resources'][resource]['treeFile'], isJSON=True)
        #print(f"ITEMS: \n {items['tree']}\n\n")
        if 'item' in items['tree']:
          self.__iterresource(resource, items['tree']['item'], customPath)
          self._saveProgressFile()
          self.__transferItems(resource)
        else:
          self.logger.info(f'There are no items to transfer for the {resource} resource')
      else:
        self.logger.info('The file path for the resource tree indicated in the progress file could not be found on the system. Going to update resource tree')
        self.getResourceTree(resource)
        self.transferResource(resource)

  def __transferItems(self, resource: str, disablePreviews: bool = True):
    resource = resource.lower()
    items = self.progress['resources'][resource]['toTransfer']
    if len(items) > 0:

      if disablePreviews:
        # Turn off Automatic Preview Generation for the API KEY
        resp = self.dest.system.SetAutomaticPreviewGeneration(createPreviews=False)
        if not resp.didSucceed():
          self.logger.error(f"There was an issue disabling the automatic preview generation for the CHILI Destination Server API Key")
        elif self.verbose:
          print(f"\n{resp.text}\n")

      itemList = items.copy()
      itemAmount = len(itemList)
      self.logger.info(f'Amount of {resource} to transfer: {itemAmount}')
      for r in itemList:
        if self.verbose:
          print(f"Name: {r['@name']}\nID: {r['@id']}\nPath: {r['@path']}\nDownload URL: {self.getDownloadURL(resource, r['@id'])}\n")

        self.logger.info(f"Checking if {resource}: {r.get('@id')} exists on destination environment")
        if self.dest.resources.doesItemExist(resource, r.get('@id')):
          self.logger.info(f"{resource}: {r.get('@id')} exists on destination environment. Skipping...")
          continue

        # Set ID for the next item
        self.logger.info(f"Setting the ID for the next uploaded item to: {r['@id']}")
        resp = self.dest.resources.setNextResourceItemID(resourceType=resource, itemID=r['@id'])
        if not resp.didSucceed():
          self.logger.error(f"There was an issue setting the next item ID for {r['@name']}: {r['@id']}\n{resp.text}")
          continue
        elif self.verbose:
          print(f"\n{resp.text}\n")

        # Extract path from resource tree item (original path is full path ending with <document name>.xml)
        if len(r['@path']) != 0:
          splitPath = r['@path'].split("\\")
          fileName = splitPath.pop()
          resourceItemPath = "\\".join(splitPath)+"\\"
        else:
          fileName = r['@name']
          resourceItemPath = ''
        print(f"Path: {resourceItemPath}")

        # If the resource is an asset or font.
        if resource == 'assets' or resource == 'fonts':

          is_truncated = True
          max_tries = 5

          while is_truncated:
            # Download the resource file data
            self.logger.info(f"Downloading asset file data temporarily for: {r['@name']}")
            fileData = self.source.resources.DownloadAsset(
              resourceType=resource,
              id=r['@id'],
              itemPath=r['@path'],
              assetType='original',
              page=1
            )
            if not resp.didSucceed():
              self.logger.error(f"There was an issue downloading the asset - Name: {r['@name']} -- Item ID: {r['@id']}\n{resp.text}")
              continue

            # Base64 Encode the byte data
            fileData = base64.b64encode(fileData.response.content)
            fileData = fileData.decode('utf-8')

            self.logger.info(f"Uploading asset data to destination CHILI server: {r['@name']}")
            resp = self.dest.resources.ResourceItemAdd(
              resourceType=resource,
              newName=fileName,
              fileData=fileData,
              xml=None,
              folderPath=resourceItemPath
            )
            if not resp.didSucceed():
              self.logger.error(f"There was an issue uploading the asset to the destination server- Name: {r['@name']} -- Item ID: {r['@id']}\n{resp.text}")
              continue

            self.logger.info(f"Comparing file sizes for - Name: {r['@name']} -- Item ID: {r['@id']}\n") 
            itemSizeDest = self.dest.resources.ResourceItemGetDefinitionXML(resourceType=resource, itemID=r['@id'])
            itemSizeSrc = self.source.resources.ResourceItemGetDefinitionXML(resourceType=resource, itemID=r['@id'])

            # Check file size
            if itemSizeSrc.data['item']['fileInfo']['@fileSize'] != itemSizeDest.data['item']['fileInfo']['@fileSize']:
              if max_tries == 0: break
              self.logger.error(f"{resource} wrong size from dest to src - Name: {r['@name']} -- Item ID: {r['@id']}\nGoing to retry {max_tries} more times.")
              self.logger.info(f"Deleting item from dest so we can re-upload it - Name: {r['@name']} -- Item ID: {r['@id']}")
              self.dest.resources.ResourceItemDelete(
                resourceType=resource,
                itemID=r['@id']
              )
              max_tries = max_tries - 1
              continue
            else:
              is_truncated = False

        elif resource == "documents":
          # Download document
          self.logger.info(f"Downloading document XML temporarily for: {r['@name']}")
          resp = self.source.resources.ResourceItemGetXML(
            resourceType='documents',
            itemID=r['@id'],
          )
          if not resp.didSucceed():
            self.logger.error(f"There was an issue downloading the document - Name: {r['@name']} -- Item ID: {r['@id']}\n{resp.text}")
            continue

          docXml = resp.text

          cd = ChiliDocument(docXml)

          # Get the DataSource ID attached to the document if there is one
          datasource_id = cd.datasource_id

          fonts = []
          for font in cd.get_fonts():
            fonts.append(font["id"])

          assets = cd.get_images()
          images = [image.get("id") for image in assets if image.get("resource_type") == "Assets"]
          daps = [image.get("id") for image in assets if image.get("resource_type") == "DynamicAssetProviders"]
          barcodes = cd.get_barcode_ids()


          if fonts:
            self.logger.info(f"Found fonts in document, transferring... (Arial Regular will probably fail)")
            self.transferList(itemList=fonts, resource="Fonts")
          if images:
            self.logger.info(f"Found images in document, transferring...")
            self.transferList(itemList=images, resource="Assets")
          if daps:
            self.logger.info(f"Found Dynamic Asset Providers in document, transferring settings for DAP...")
            self.transferList(itemList=daps, resource="DynamicAssetProviders")
          if barcodes:
            self.logger.info(f"Found Barcode frames in document, transferring Barcode settings...")
            self.transferList(itemList=barcodes, resource="BarcodeTypes")
          if datasource_id:
            self.logger.info(f"Found DataSource attached to document, transferring DataSource settings")
            self.transferList(itemList=[datasource_id], resource="DataSources")

          # Create a placeholder document because if you ResourceItemAdd a document, CHILI will process the XML and will remove spaces
          self.logger.info(f"Creating placeholder document to destination CHILI server: {r['@name']}")
          resp = self.dest.resources.ResourceItemAdd(
            resourceType='documents',
            newName=fileName,
            folderPath=resourceItemPath,
            xml='<document />'
          )
          if not resp.didSucceed():
            self.logger.error(f"There was an issue creating a placeholder document to the destination server- Name: {r['@name']} -- Item ID: {r['@id']}\n{resp.text}")
            continue

          # CHILI loves blank documents so retry until it's not blank
          blank_doc = True

          while blank_doc:
            self.logger.info(f"Uploading document data to destination CHILI server: {r['@name']}")
            resp = self.dest.resources.ResourceItemSave(
              resourceType="documents",
              itemID=r['@id'],
              xml=docXml,
            )
            if not resp.didSucceed():
              self.logger.error(f"There was an issue uploading the document to the destination server- Name: {r['@name']} -- Item ID: {r['@id']}\n{resp.text}")
              break

            self.logger.info(f"Processing document server side: {r['@name']}")
            resp = self.dest.documents.processServerSide(
              documentID=r['@id']
            )
            sleep(1)

            self.logger.info(f"Checking if uploading doc is blank: {r['@name']}")
            resp = self.dest.resources.ResourceItemGetXML(
              resourceType="documents",
              itemID=r['@id'])
            if not resp.didSucceed():
              self.logger.error(f"There was an issue getting the document XML for the blank document check- Name: {r['@name']} -- Item ID: {r['@id']}\n{resp.text}")
              break

            blank_doc = self.dest.documents.is_blank(resp.text)
            if blank_doc: self.logger.info(f"Uploaded document was blank. Going to retry the ResourceItemSave{r['@name']}")
            else: self.logger.info(f"Uploaded document is not blank")

        # Item is not a document, asset, or font
        else:
          # Get the item XML (I think only assets and fonts are using fileData)
          resp = self.source.resources.ResourceItemGetXML(resourceType=resource, itemID=r['@id'])
          if not resp.didSucceed():
            self.logger.error(f"There was an issue getting the item XML - Name: {r['@name']} -- Item ID: {r['@id']}\n{resp.text}")
            continue
          elif self.verbose:
            print(f"\n{resp.text}\n")

          item_xml = resp.text

          resp = self.dest.resources.ResourceItemAdd(
            resourceType=resource,
            newName=r['@name'],
            folderPath=resourceItemPath,
            xml=item_xml
          )
          if not resp.didSucceed():
            self.logger.error(f"There was an issue adding the item - Name: {r['@name']} -- Item ID: {r['@id']}\n{resp.text}")
            continue
          elif self.verbose:
            print(f"\n{resp.text}\n")

        # Set a pause to avoid overwhelming the server.
        self.logger.info(f"Successfully transferred Name: {r['@name']} - ID: {r['@id']} to the destination CHILI server.")
        itemAmount = itemAmount - 1
        self.logger.info(f"Waiting {self.interval} seconds to avoid server stress. There are {itemAmount} resources left")
        self.progress['resources'][resource]['toTransfer'].remove(r)
        self._saveProgressFile()
        sleep(self.interval)

      if disablePreviews:
        # Turn back on the Automatic Preview Generation for the API KEY
        resp = self.dest.system.SetAutomaticPreviewGeneration(createPreviews=True)
        if not resp.didSucceed():
          self.logger.error(f"There was an issue re-enabling the automatic preview generation for the CHILI Destination Server API Key")
        elif self.verbose:
          print(f"\n{resp.text}\n")

    else:
      self.logger.info(f'There is nothing queued to transfer for the {resource} resource')


  def __iterresource(self, resource: str, d, customPath: str = None):
    for v in d:
      # Folder item is going to be a list
      # file item is going to be a dict with the info
      if isinstance(v, dict):
        if '@isFolder' in v.keys():
          if v['@isFolder'] == 'true':
            if 'item' in v.keys():
              if isinstance(v['item'], dict): v['item'] = [v['item']]
              self.__iterresource(resource, v['item'])
            else:
              #Empty folder
              pass
          else:
            if customPath is not None:
              v['@path'] = customPath
            self.progress['resources'][resource]['toTransfer'].append(v)
            if self.verbose:
              self.logger.info(f"Adding {v} to the transfer queue")
      elif isinstance(v, str):
        if isinstance(d[v], list):
          self.__iterresource(resource, d[v])

  def getDownloadURL(self, resource: str, itemID: str):
    downloadURL =  self.source.baseURL + self.source.environment + '/download.aspx?type=original&resourceName=' + resource + '&id=' + itemID + '&apiKey=' + self.source.getAPIKey() + '&pageNum=1'
    return downloadURL

  def _saveProgressFile(self):
    writeFile(fileName=self.progressFile, data=self.progress, isJSON=True)