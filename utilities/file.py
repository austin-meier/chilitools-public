from __future__ import annotations
import requests
import json
from base64 import b64encode
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from chilitools.api.connector import ChiliConnector

from os.path import isfile, dirname, realpath, sep, getsize
from os import makedirs
from chilitools.utilities.errors import ErrorHandler
from chilitools.utilities.strings import convertFileSize
from chilitools.utilities.xmltools import getTaskResultURL, removeTimelineTags
from chilitools.utilities.defaults import DEFAULT_TASKPRIORITY

def currentPath(file: str) -> str:
  return dirname(realpath(file))

def getBase64String(filePath: str = None, fileBytes: bytes = None) -> str:
  """Returns a string of the base64 encoded file bytes.
  You can pass fileBytes directly or a file path to the file you would like to encode

  :type filePath: str
  :type fileBytes: bytes
  """
  if fileBytes and filePath is None:
    return 'You must provide a file path or file bytes for this function'
  if filePath is not None:
    with open(filePath, 'rb') as file:
      fileBytes = file.read()
  fileData = b64encode(fileBytes)
  return fileData.decode('utf-8')

def readFile(fileName: str, isJSON: bool = False, encoding: str = None):
  if checkForFile(fileName=fileName):
    with open(fileName, 'r', encoding=encoding) as file:
      if isJSON:
        return json.loads(file.read())
      else:
        return file.read()
  else:
    return ErrorHandler().getError(errorName="FILENOTFOUND")

def writeFile(fileName: str, data, isJSON: bool = False, encoding: str = None) -> None:
  makedirs(dirname(fileName), exist_ok=True)
  with open(fileName, 'w', encoding=encoding) as file:
    if isJSON:
      file.write(json.dumps(data))
    else:
      file.write(data)

def checkForFile(fileName: str) -> bool:
  if isfile(fileName):
    return True
  return False

def removeTimelineFromDocFile(fileName: str, outputFolder: str, verbose: bool = False) -> str:
  # try:
    print(f"File size before stripping tags: {convertFileSize(getsize(fileName), 'kb')}")
    with open(file=fileName, mode='r') as file:
      docXML = file.read()
    docXML = removeTimelineTags(docXML=docXML, verbose=verbose)
    # sep = os.path.sep
    path = fileName.split(sep)
    fileName = path.pop().split('.xml')[0]
    outputFile = sep.join(path) + sep + outputFolder + fileName + '.xml'
    makedirs(dirname(outputFile), exist_ok=True)
    with open(file=outputFile, mode='w', encoding='utf-8') as file:
      file.write(docXML)
    print(f"File size after stripping tags: {convertFileSize(getsize(outputFile), 'kb')}")
    return 'Successfully stripped timeline tags from document XML'
  # except Exception as e:
  #   return f'There was an issue removing the timeline docs: {e}'

def downloadFile(url: str, fullFileName: str, queryParams: dict = None) -> bool:
  if queryParams is None: queryParams = {}
  try:
    download = requests.get(url=url, allow_redirects=True, params=queryParams)
    open(fullFileName, 'wb').write(download.content)
    return True
  except Exception as e:
    print(e)
    return False

def generateAndDownloadPDF(connector: ChiliConnector, fullFileName: str, documentID: str = None, documentXML: str = None, settingsXML: str = None, settingsID: str = None, taskPriority: int = DEFAULT_TASKPRIORITY, verbose: bool = False, downloadXML: bool = False) -> str:

  if documentID is None and documentXML is None:
    return 'You need to provide a document ID or document XML parameter'

  if settingsID is None and settingsXML is None:
    return "You need to provide a PDF Export Settings Item ID or PDF Export Settings XML"
  
  if downloadXML is True and documentID is not None:
    if verbose: print("Downloading XML for document")
    resp = connector.resources.ResourceItemGetXML(
      resourceType="documents",
      itemID=documentID
    )
    if not resp.didSucceed:
      return "There was a problem getting the XML for the document"
    documentXML = resp.text
    documentID = None

  if settingsID is not None:
    print(f"Getting PDF Export Settings XML for {settingsID}")
    settingsXML = connector.resources.getPDFSettingsXML(settingsID=settingsID).text

  if documentID is not None:
    resp = connector.makeRequest(
      method='post',
      endpoint=f"/resources/documents/{documentID}/representations/pdf",
      queryParams={'taskPriority':taskPriority},
      json={'settingsXML':settingsXML}
    )
  elif documentXML is not None:
    resp = connector.documents.createTempPDF(documentXML=documentXML, settingsXML=settingsXML)
  if verbose: print(resp.text)
  if resp.didSucceed():
    with open("C:\\Users\\Austin\\Desktop\\python_request.txt", "w") as file:
      file.write(resp.response.request.body.decode('utf-8'))
    taskID = resp.contentAsDict()['task']['@id']
    task = connector.system.waitForTask(taskID=taskID, debug=verbose)
    resultURL = getTaskResultURL(task=task)
    if resultURL == ErrorHandler().getError(errorName="TASKNOTSUCCEEDED"):
      return False
    success = downloadFile(url=resultURL, fullFileName=fullFileName)
    print(f"URL: {getTaskResultURL(task=task)}")
    if success:
      return (f"The file successfully downloaded to {fullFileName}")
    return "The file download process failed."

def createAndDownloadImages(connector: ChiliConnector, documentID: str, imageConversionProfileID: str, settingsXML: str, taskPriority: int = DEFAULT_TASKPRIORITY):
  resp = connector.makeRequest(
    method='post',
    endpoint=f"resources/documents/{documentID}/representations/images",
    queryParams={'imageConversionProfileID':imageConversionProfileID, 'taskPriority':taskPriority},
    json={'settingsXML':settingsXML}
  )
  if resp.didSucceed():
    taskID = resp.contentAsDict()['task']['@id']
    task = connector.system.waitForTask(taskID=taskID)
    return task
  return f"Request to make images failed: {resp.text}"
