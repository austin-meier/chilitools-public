from __future__ import annotations
from typing import TYPE_CHECKING, OrderedDict
from urllib import request
if TYPE_CHECKING:
    from chilitools.api.connector import ChiliConnector
    from chilitools.api.response import ChiliResponse

from time import sleep
from chilitools.api.mycp import generateLoginTokenForURL, getCredentials
from chilitools.utilities.errors import ErrorHandler
from chilitools.utilities.file import getBase64String
from chilitools.utilities.defaults import DEFAULT_TASKPRIORITY, DEFAULT_TASKUPDATETIME, STAFF_TYPE, USER_TYPE

class Resources:
  def __init__(self, connector: ChiliConnector):
    self.connector = connector
  def DownloadTempFile(self, assetType: str, path: str = '', data: str = '', dynamicAssetProviderID: str = '', noContentHeader: bool = None) -> ChiliResponse:
    return self.connector.makeRequest(
      method='get',
      endpoint=f"/resources/{assetType}/download/tempfile",
      queryParams={'path':path, 'data':data, 'dynamicAssetProviderID':dynamicAssetProviderID, 'noContentHeader':noContentHeader}
    )
  def ResourceItemGetHistory(self, resourceType: str, itemID: str) -> ChiliResponse:
    return self.connector.makeRequest(
      method='get',
      endpoint=f"/resources/{resourceType}/items/{itemID}/history"
    )
  def ResourceItemResetPreviews(self, resourceType: str, itemID: str) -> ChiliResponse:
    return self.connector.makeRequest(
      method='delete',
      endpoint=f"/resources/{resourceType}/items/{itemID}/previews"
    )
  def ResourceItemPreviewOverride(self, resourceType: str, itemID: str) -> ChiliResponse:
    return self.connector.makeRequest(
      method='delete',
      endpoint=f"/resources/{resourceType}/items/{itemID}/previewoverride"
    )
  def ResourceItemReplaceFile(self, resourceType: str, itemID: str, fileData: str) -> ChiliResponse:
    return self.connector.makeRequest(
      method="put",
      endpoint=f"/resources/{resourceType}/items/{itemID}/file",
      json={'fileData': fileData}
    )
  def ResourceItemReplaceFileWithPreviewOverride(self, resourceType: str, itemID: str, fileData: str, previewExtension: str, isPermanentPreview: bool) -> ChiliResponse:
    return self.connector.makeRequest(
      method="put",
      endpoint=f"/resources/{resourceType}/items/{itemID}/filewithpreview",
      queryParams={'previewExtension':previewExtension, 'isPermanentPreview':isPermanentPreview},
      json={'fileData':fileData, 'previewFileData': fileData}
    )
  def ResourceItemMove(self, resourceType: str, itemID: str, newName: str, newFolderPath: str) -> ChiliResponse:
    return self.connector.makeRequest(
      method='put',
      endpoint=f"/resources/{resourceType}/items/{itemID}/move",
      queryParams={'newName':newName, 'newFolderPath':newFolderPath}
    )
  def ResourceItemCopy(self, resourceType: str, itemID: str, newName: str, folderPath: str = '') -> ChiliResponse:
    return self.connector.makeRequest(
      method='post',
      endpoint=f"/resources/{resourceType}/items/{itemID}/copy",
      queryParams={'newName':newName, 'folderPath':folderPath },
    )
  def ResourceItemDelete(self, resourceType: str, itemID: str) -> ChiliResponse:
    return self.connector.makeRequest(
      method='delete',
      endpoint=f"/resources/{resourceType}/items/{itemID}",
    )
  def ResourceItemSave(self, resourceType: str, itemID: str, xml: str) -> ChiliResponse:
    return self.connector.makeRequest(
      method='put',
      endpoint=f"/resources/{resourceType}/items/{itemID}/save",
      json={'xml':xml}
    )
  def ResourceItemGetXML(self, resourceType: str, itemID: str) -> ChiliResponse:
    return self.connector.makeRequest(
      method='get',
      endpoint=f"/resources/{resourceType}/items/{itemID}/xml"
    )
  def ResourceItemGetURL(self, resourceType: str, itemID: str, URLtype: str, pageNum: int = 1) -> ChiliResponse:
    return self.connector.makeRequest(
      method='get',
      endpoint=f"/resources/{resourceType}/items/{itemID}/url",
      queryParams={'type':URLtype, 'pageNum':pageNum},
    )
  def uploadAsset(self, newName: str, folderPath: str, assetFilePath: str) -> ChiliResponse:
    return self.ResourceItemAdd(
      resourceType='assets',
      newName=newName,
      folderPath=folderPath,
      xml = '',
      fileData=getBase64String(filePath=assetFilePath)
    )
  def ResourceItemAdd(self, resourceType: str, newName: str, folderPath: str, xml: str, fileData: str = '') -> ChiliResponse:
    return self.connector.makeRequest(
      method='post',
      endpoint=f"/resources/{resourceType}/items",
      queryParams={'newName':newName, 'folderPath':folderPath},
      json={'xml':xml, 'fileData':fileData}
    )
  def ResourceItemAddFromURL(self, resourceType: str, newName: str, folderPath: str, url: str, authUsername: str = None, authPassword: str = None, reuseExisting: bool = None, previewFileURL: str = None, previewExtension: str = None, isPermanentPreview: bool = None) -> ChiliResponse:
    return self.connector.makeRequest(
      method='post',
      endpoint=f"/resources/{resourceType}/items/fromurl",
      queryParams={'newName':newName, 'folderPath':folderPath, 'url':url, 'login':authUsername, 'pw':authPassword, 'reuseExisting':reuseExisting, 'previewFileURL':previewFileURL, 'previewExtension':previewExtension, 'isPermanentPreview':isPermanentPreview },
    )
  def ResourceGetTreeLevel(self, resourceType: str, parentFolder: str = '', numLevels: int = 1, includeSubDirectories: bool = True, includeFiles: bool = True) -> ChiliResponse:
    return self.connector.makeRequest(
      method='get',
      endpoint=f"/resources/{resourceType}/treelevel",
      queryParams={'parentFolder':parentFolder, 'numLevels':numLevels, 'includeSubDirectories':includeSubDirectories, 'includeFiles':includeFiles}
    )
  async def AsyncResourceGetTreeLevel(self, resourceType: str, parentFolder: str = '', numLevels: int = 1, includeSubDirectories: bool = True, includeFiles: bool = True) -> ChiliResponse:
    return self.connector.makeRequest(
      method='get',
      endpoint=f"/resources/{resourceType}/treelevel",
      queryParams={'parentFolder':parentFolder, 'numLevels':numLevels, 'includeSubDirectories':includeSubDirectories, 'includeFiles':includeFiles}
    )
  def ResourceGetTree(self, resourceType: str, parentFolder: str = '', includeSubDirectories: bool = 'False', includeFiles: bool = True) -> ChiliResponse:
    return self.connector.makeRequest(
      method='get',
      endpoint=f"/resources/{resourceType}/tree",
      queryParams={'parentFolder':parentFolder, 'includeSubDirectories':includeSubDirectories, 'includeFiles':includeFiles}
    )
  def ResourceSearch(self, resourceType: str, name: str = '') -> ChiliResponse:
    return self.connector.makeRequest(
      method='get',
      endpoint=f"/resources/{resourceType}",
      queryParams={'name':name}
    )
  def ResourceItemGetDefinitionXML(self, resourceType: str, itemID: str)-> ChiliResponse:
    return self.connector.makeRequest(
      method='get',
      endpoint=f"/resources/{resourceType}/items/{itemID}/definitionxml"
    )
  def ResourceFolderAdd(self, resourceType: str, newName: str, parentPath: str = None) -> ChiliResponse:
    return self.connector.makeRequest(
      method='post',
      endpoint=f"/resources/{resourceType}/folders",
      queryParams={'newName':newName, 'parentPath':parentPath}
    )
  def ResourceFolderDelete(self, resourceType: str, relativePath: str) -> ChiliResponse:
    return self.connector.makeRequest(
      method='delete',
      endpoint=f"/resources/{resourceType}/folders",
      queryParams={'relativePath':relativePath}
    )
  def ResourceFolderMove(self, resourceType: str, folderPath: str, newFolderPath: str) -> ChiliResponse:
    return self.connector.makeRequest(
      method='put',
      endpoint=f"/resources/{resourceType}/folders/move",
      queryParams={'folderPath':folderPath, 'newFolderPath':newFolderPath}
    )
  def ResourceFolderCopy(self, resourceType: str, folderPath: str, newFolderPath: str, includeSubFolders: bool) -> ChiliResponse:
    return self.connector.makeRequest(
        method='post',
        endpoint=f"/resources/{resourceType}/folders/copy",
        queryParams={'folderPath':folderPath, 'newFolderPath':newFolderPath, 'includeSubFolders':includeSubFolders}
      )
  def DownloadAsset(self, resourceType: str, id: str, itemPath: str = None, name: str = None, assetType: str = None, page: int = None, docID: str = None, taskPriority: int = DEFAULT_TASKPRIORITY) -> ChiliResponse:
    return self.connector.makeRequest(
      method='get',
      endpoint=f"/resources/{resourceType}/download",
      queryParams={'id':id, 'path':itemPath, 'name':name, 'type':assetType, 'page':page, 'docId':docID, 'taskPriority':taskPriority}
    )
  def getPDFSettingsXML(self, settingsID: str) -> ChiliResponse:
    return self.connector.makeRequest(
      method='get',
      endpoint=f"/resources/PdfExportSettings/items/{settingsID}/xml"
    )
  def setNextResourceItemID(self, resourceType: str, itemID: str) -> ChiliResponse:
    return self.connector.makeRequest(
      method='post',
      endpoint=f"/resources/{resourceType}/nextitemid",
      queryParams={'itemID':itemID}
    )
  def getResourceList(self) -> ChiliResponse:
    return self.connector.makeRequest(
      method='get',
      endpoint=f"/resources"
    )
  def addFolder(self, resourceType: str, newFolderPath: str) -> ChiliResponse:
    splitFolder = newFolderPath.split('/')
    folderPath = '/'.join(splitFolder[:-1])+'/'
    folderName = splitFolder[-1]
    return self.ResourceFolderAdd(
      resourceType=resourceType,
      newName=folderName,
      parentPath=folderPath,
      )
  def getDownloadURL(self, resourceType: str, itemID: str, pageNum: int = 1) -> ChiliResponse:
    return 'https://' + self.connector.baseURL + '/' + self.connector.enviroment + '/download.aspx?type=original&resourceName=' + resourceType + '&id=' + itemID + '&apiKey=' + self.connector.getAPIKey() + '&pageNum=' + pageNum

  def getFullResourceTree(self, resourceType: str, folder: str = '') -> dict:
    items = dict()
    return self._resourceTreeIter(resourceType, items, folder=folder)

  def get_items_in_tree(self, resourceType: str, folder: str = '') -> list:
    items = list()
    return self._resourceItemsIter(resourceType, items, folder=folder)

  def _resourceTreeIter(self, resourceType: str, itemsDict: dict, folder: str = '') -> dict:

    resp = self.ResourceGetTreeLevel(
      resourceType=resourceType,
      parentFolder=folder,
      numLevels=1,
      includeSubDirectories=True,
      includeFiles=True
    )

    items = resp.content['tree'].get('item')

    if items is not None:
      if not isinstance(items, list): items = [items]
      for item in items:
        if item['@isFolder'] == 'true':
          print(f"Going in to folder {item['@name']}")
          itemsDict[item['@name']] = {}
          self._resourceTreeIter(resourceType, itemsDict[item['@name']], item['@path'])
        else:
          itemsDict[item['@name']] = item
    return itemsDict

  def _resourceItemsIter(self, resourceType: str, items_list: list = None, folder: str = '') -> list:

    resp = self.ResourceGetTreeLevel(
      resourceType=resourceType,
      parentFolder=folder,
      numLevels=1,
      includeSubDirectories=True,
      includeFiles=True
    )

    items = resp.content['tree'].get('item')

    if items is not None:
      if not isinstance(items, list):
        items = [items]
      for item in items:
        if item['@isFolder'] == 'true':
          self._resourceItemsIter(resourceType, items_list, item['@path'])
        else:
          items_list.append(item)
    return items_list


class Documents:
  def __init__(self, connector: ChiliConnector):
    self.connector = connector

  def setAssetDirectories(self, documentID: str, userAssetDirectory: str, userGroupAssetDirectory: str, documentAssetDirectory: str) -> ChiliResponse:
    return self.connector.makeRequest(
      method='post',
      endpoint=f"/resources/documents/{documentID}/assetdirectories",
      queryParams={'userAssetDirectory':userAssetDirectory, 'userGroupAssetDirectory':userGroupAssetDirectory, 'documentAssetDirectory':documentAssetDirectory },
    )
  def setDataSource(self, documentID: str, datasourceXML: str) -> ChiliResponse:
    return self.connector.makeRequest(
      method="post",
      endpoint=f"/resources/documents/{documentID}/datasource",
      json={'datasourceXML':datasourceXML}
    )
  def getInfo(self, documentID: str, extended: bool = False) -> ChiliResponse:
    return self.connector.makeRequest(
      method='get',
      endpoint=f"/resources/documents/{documentID}/info",
      queryParams={'extended':extended}
    )
  def getVariableDefinitions(self, documentID: str) -> ChiliResponse:
    return self.connector.makeRequest(
      method='get',
      endpoint=f"/resources/documents/{documentID}/variabledefinitions"
    )
  def setVariableDefinitions(self, documentID: str, definitionXML: str, replaceExisitingVariables: bool = False) -> ChiliResponse:
    return self.connector.makeRequest(
      method='post',
      endpoint=f"/resources/documents/{documentID}/variabledefinitions",
      queryParams={'replaceExistingVariables':replaceExisitingVariables},
      json={'definitionXML':definitionXML}
    )
  def getVariableValues(self, documentID: str) -> ChiliResponse:
    return self.connector.makeRequest(
      method='get',
      endpoint=f"/resources/documents/{documentID}/variablevalues"
    )
  def setVariableValues(self, documentID: str, variableXML: str) -> ChiliResponse:
    return self.connector.makeRequest(
      method='post',
      endpoint=f"/resources/documents/{documentID}/variablevalues",
      json={'varXML':variableXML}
    )
  def delete(self, documentID: str) -> ChiliResponse:
    return self.connector.resources.ResourceItemDelete(resourceType='documents', itemID=documentID)
  def getPreviewURL(self, documentID: str, URLtype: str = 'full', pageNum: int = 1):
    return self.connector.makeRequest(
      method='get',
      endpoint=f"/resources/documents/items/{documentID}/url",
      queryParams={'type':URLtype, 'pageNum':pageNum},
    )
  def getEditorURL(self, documentID: str, workSpaceID: str = None, viewPrefsID: str = None, constraintsID: str = None, viewerOnly: bool = None, forAnonymousUser: bool = None) -> ChiliResponse:
    return self.connector.makeRequest(
      method='get',
      endpoint=f"/resources/documents/{documentID}/urls/editor",
      queryParams={'workSpaceID':workSpaceID, 'viewPrefsID':viewPrefsID, 'constraintsID':constraintsID, 'viewerOnly':viewerOnly, 'forAnonymousUser':forAnonymousUser}
    )
  def getXML(self, documentID: str) -> ChiliResponse:
    return self.connector.makeRequest(
      method='get',
      endpoint=f"/resources/documents/items/{documentID}/xml"
    )
  def saveXML(self, documentID: str, docXML: str) -> ChiliResponse:
    return self.connector.makeRequest(
      method='put',
      endpoint=f"/resources/documents/items/{documentID}/save",
      json={'xml':docXML}
    )
  def getVariableValues(self, documentID: str) -> ChiliResponse:
    return self.connector.makeRequest(
      method='get',
      endpoint=f"/resources/documents/{documentID}/variablevalues"
    )
  def setVariableValues(self, documentID: str, varXML: str) -> ChiliResponse:
    return self.connector.makeRequest(
      method='post',
      endpoint=f"/resources/documents/{documentID}/variablevalues",
      json={'varXML':varXML}
    )
  def createPDF(self, documentID: str, settingsXML: str = None, settingsID: str = None, taskPriority: int = DEFAULT_TASKPRIORITY) -> ChiliResponse:
    if settingsID is None and settingsXML is None:
      return
    if settingsID is not None:
      settingsXML = self.connector.resources.getPDFSettingsXML(settingsID=settingsID).text
    return self.connector.makeRequest(
      method='post',
      endpoint=f"/resources/documents/{documentID}/representations/pdf",
      queryParams={'taskPriority':taskPriority},
      json={'settingsXML':settingsXML}
    )
  def createTempPDF(self, documentXML: str, settingsXML: str = None, settingsID: str = None, itemID: str = None, taskPriority: int = DEFAULT_TASKPRIORITY) -> ChiliResponse:
    if settingsID is None and settingsXML is None:
      return
    if settingsID is not None:
      settingsXML = self.resources.getPDFSettingsXML(settingsID=settingsID).text
    return self.connector.makeRequest(
      method='post',
      endpoint=f"/resources/documents/tempxml/pdf",
      queryParams={'itemID':itemID, 'taskPriority':taskPriority},
      json={'settingsXML':settingsXML, 'docXML':documentXML}
    )
  def createImages(self, documentID: str, imageConversionProfileID: str, settingsXML: str = None, settingsID: str = None, taskPriority: int = DEFAULT_TASKPRIORITY) -> ChiliResponse:
    if settingsID is None and settingsXML is None:
      return
    if settingsID is not None:
      settingsXML = self.resources.getPDFSettingsXML(settingsID=settingsID).text
    return self.connector.makeRequest(
      method='post',
      endpoint=f"/resources/documents/{documentID}/representations/images",
      queryParams={'imageConversionProfileID':imageConversionProfileID, 'taskPriority':taskPriority},
      json={'settingsXML':settingsXML}
    )
  def createTempImages(self, imageConversionProfileID: str, documentID: str = None, documentXML: str = '', settingsXML: str = None, settingsID: str = None, taskPriority: int = DEFAULT_TASKPRIORITY) -> ChiliResponse:
    if settingsID is None and settingsXML is None:
      return
    if documentID is None and documentXML is None:
      return
    if settingsID is not None:
      settingsXML = self.resources.getPDFSettingsXML(settingsID=settingsID).text
    return self.connector.makeRequest(
      method='post',
      endpoint=f"/resources/documents/tempxml/images",
      queryParams={'imageConversionProfileID':imageConversionProfileID, 'itemID':documentID, 'taskPriority':taskPriority},
      json={'settingsXML':settingsXML, 'docXML':documentXML}
    )
  def processServerSide(self, documentID: str) -> ChiliResponse:
    return self.connector.makeRequest(
    method='put',
    endpoint=f"/resources/documents/documentprocessor",
    json={'itemID':documentID, 'resourceXML':''}
  )

class System:
  def __init__(self, connector: ChiliConnector):
    self.connector = connector

  def getTaskStatus(self, taskID: str) -> ChiliResponse:
    return self.connector.makeRequest(
      method='get',
      endpoint=f"/system/tasks/{taskID}/status"
    )
  def waitForTask(self, taskID: str, taskUpdateTime: int = DEFAULT_TASKUPDATETIME, debug: bool = False) -> OrderedDict:
    while True:
      resp = self.getTaskStatus(taskID=taskID).contentAsDict()
      taskStatus = resp['task']['@finished']
      if debug: print(f"Polled Task: Current Status: {taskStatus}")
      if taskStatus == "True":
        return resp
      sleep(taskUpdateTime)

  def GenerateApiKey(self, username: str = None, password: str = None) -> ChiliResponse:
    if not username or not password:
      # We need to get their credentials
      login = getCredentials()

      if login["type"] == STAFF_TYPE:
        username = "ChiliAdmin"
        password = generateLoginTokenForURL(backofficeURL=self.connector.backofficeURL)
      else:
        username = login["credentials"]["Username"]
        password = login["credentials"]["Password"]

      requestJSON = {'userName':username, 'password': password}

    # Request
    return self.connector.makeRequest(
      method='post',
      endpoint='/system/apikey',
      queryParams={'environmentNameOrURL': self.connector.getEnvironment()},
      json=requestJSON,
      authRequired=False
    )

  def SetAutomaticPreviewGeneration(self, createPreviews: bool) -> ChiliResponse:
    return self.connector.makeRequest(
      method='put',
      endpoint='system/apikey/autopreviewgeneration',
      queryParams={'createPreviews':createPreviews}
    )

