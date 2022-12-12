from operator import truediv
import requests
from os import getenv, remove
from os.path import exists
from chilitools.settings.config import LOGIN_FILE
from chilitools.utilities.defaults import STAFF_TYPE, USER_TYPE
from chilitools.utilities.file import checkForFile, readFile, writeFile


def getCredentials() -> dict:
  if getenv('CHILI_PUBLISH_USERNAME') is not None and getenv('CHILI_PUBLISH_PASSWORD') is not None:
    login = {'type':STAFF_TYPE, 'credentials': { 'Username': getenv('CHILI_PUBLISH_USERNAME'), 'Password': getenv('CHILI_PUBLISH_PASSWORD') }}
  elif checkForFile(fileName=LOGIN_FILE):
    # Login was found in file, lets load it
    login = readFile(fileName=LOGIN_FILE, isJSON=True)
  else:
    # Login not created yet, let's create one
    login = inputCredentials()
  return login

def formatLogin(username: str, password: str, login_type: str = USER_TYPE) -> str:
  return {'type':login_type, 'credentials': { 'Username': username, 'Password': password }}

def writeLoginFile(login_info: dict) -> bool:
  try:
    writeFile(fileName=LOGIN_FILE, data=login_info, isJSON=True)
    return True
  except Exception as e:
    print("There was an issue writing the login file")
    return False

def deleteLoginFile() -> bool:
  try:
    if exists(LOGIN_FILE):
      remove(LOGIN_FILE)
    return True
  except Exception as e:
    print(f"There was an issue deleting the login file: {e}")
    return False

def inputCredentials() -> dict:
  print("Please enter your CHILI username")
  username = input().strip()
  print("Please enter your CHILI password")
  password = input().strip()
  login_type = STAFF_TYPE if "@" in username else USER_TYPE
  if login_type == STAFF_TYPE: print("Staff account detected, configuring login details for staff login syntax")
  login = formatLogin(username=username, password=password, login_type=login_type)
  writeLoginFile(login_info=login)
  return login

def setUserType(userType: str) -> bool:
  if checkForFile(fileName=LOGIN_FILE):
    login = readFile(fileName=LOGIN_FILE, isJSON=True)
    login['type'] = userType
  writeFile(fileName=LOGIN_FILE, data=login, isJSON=True)

def generateOAuthTokenFromCredentials(login: dict = None) -> str:
  if login is None: login = getCredentials()
  if login['type'] == STAFF_TYPE:

    requestURL = "https://my.chili-publish.com/api/v1/auth/login"

    requestHeaders = {
        "Content-Type":"application/json",
        "accept": "*/*"
    }
    response = requests.post(url=requestURL, headers=requestHeaders, json=login['credentials'])

    if response.status_code != 200:
      return f"There was an error generating an OAuth Bearer Token. Status Code: {response.status_code}. Text: {response.text}"
    else:
      return response.json()['token']
  return "This method uses Azure AD OAuth login and is reserved for CHILI Staff"

def generateLoginTokenForURL(backofficeURL: str) -> str:
  login = getCredentials()
  if login['type'] == STAFF_TYPE:
    requestURL = "https://my.chili-publish.com/api/v1/backoffice/generate"

    requestHeaders = {
      "content-type":"application/json",
      "accept": "*/*",
      "authorization": "Bearer " + generateOAuthTokenFromCredentials(login=login)
    }

    requestJSON = {
      "Url":backofficeURL
    }

    response = requests.post(url=requestURL, headers=requestHeaders, json=requestJSON)

    if response.status_code != 200:
      return f"There was an error generating an login token. Status Code: {response.status_code}. Text: {response.text}"
    else:
      return response.json()['token']
  return "This method uses Azure AD OAuth login and is reserved for CHILI Staff"

