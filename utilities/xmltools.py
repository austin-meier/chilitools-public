import re
import xmltodict
from chilitools.utilities.errors import ErrorHandler
from xml.sax.saxutils import unescape
from xml.etree.ElementTree import Element, SubElement, tostring
from bs4 import BeautifulSoup

#TODO FIX THE 'xml' package import problem conflicting with the xml.py filename

illegalXMLCharacters = re.compile(u'[\x00-\x08\x0b\x0c\x0e-\x1F\uD800-\uDFFF\uFFFE\uFFFF]')

def sanitizeAndUpload(chiliConnector, newName: str, folderPath: str, xml: str, strict: bool = False):
  xml = cleanXML(xml)
  xml = removeSpaces(xml)
  if strict: xml = sanitize_text(xml).decode('utf-8')
  return chiliConnector.resources.ResourceItemAdd(
    resourceType='documents',
    newName=newName,
    folderPath=folderPath,
    xml=xml
  )

def unescapeXML(xmlString: str) -> str:
  return unescape(xmlString, {'&quot;':'\"'})

def parseXML(xmlString: str):
  return xmltodict.parse(xmlString)

def cleanXML(val: str, replacement: str = '') -> str:
  return illegalXMLCharacters.sub(replacement, val)

def removeSpaces(xmlString: str) -> str:
  return xmlString.replace(u'\u200b', '').replace(u'\xa0', '').replace(u'\ufeff', '')

def getIllegalChars(xmlString: str) -> list:
  return [c for c in xmlString if ord(c) >= 127]

def sanitize_text(data: str, verbose: bool = False):
  replace_with = {
    u'\u2018': '\'',
    u'\u2019': '\'',
    u'\u201c': '"',
    u'\u201d': '"'
  }

  bad_chars = [c for c in data if ord(c) >= 127]
  if bad_chars and verbose:
    print('INVALID CHARACTERS: {}'.format(bad_chars))
  else:
    print('INVALID CHARACTERS: {}'.format(bad_chars))

  for uni_char in replace_with.keys():
    data = data.replace(uni_char, replace_with.get(uni_char))

  data = ''.join([c for c in data if ord(c) < 127])
  return data.encode('utf-8', 'xmlcharreplace')

def createDatasourceXML(dataSourceID: str, data: list) -> str:
  numChildren = len(data)
  root = Element('dataSource', {'dataSourceID':dataSourceID, 'hasContent':'true', 'numRows':str(numChildren)})
  for r in range(numChildren):
    row = SubElement(root, 'row', {'rowNum':str(r+1)})
    c = 1
    for key, value in data[r].items():
      col = SubElement(row, 'col'+str(c), {'varName':key})
      col.text = str(value)
      c += 1
  return tostring(root, encoding='unicode')

def taskWasSuccessfull(task) -> bool:
  if task['task']['@succeeded'] == "True":
    return True
  return False

def getTaskResultURL(task) -> str:
  if taskWasSuccessfull(task=task):
    result = task['task']['@result']
    result = unescapeXML(result)
    result = parseXML(result)
    return result['result']['@url']
  return ErrorHandler().getError(errorName="TASKNOTSUCCEEDED")

def removeTimelineTags(docXML: str, verbose: bool = False):
  doc = BeautifulSoup(docXML, 'xml')
  #if verbose: print(f"Size of doc before: {len(str(doc))}")
  doc = _stripTimelineTag(doc=doc, verbose=verbose)
  #if verbose: print(f"Size of doc after: {len(newDoc)}")
  return doc

def _stripTimelineTag(doc, verbose: bool = False):
  if doc.timeline is not None:
    if verbose: print("Found some timeline tags, stripping them")
    doc.timeline.decompose()
  snippets = doc.find_all('item', attrs={'snippetDocXML':True})

  for snippet in snippets:
    if verbose: print("Found a snippet, checking for tags in there")
    snippet['snippetDocXML'] = _stripTimelineTag(BeautifulSoup(snippet['snippetDocXML'], 'xml'), verbose=verbose)
  return str(doc)