__version__ = '0.1.69'

import re
import pyperclip as pc
from chilitools.utilities.backoffice import backofficeURLInput
from chilitools.api.connector import ChiliConnector
from chilitools.api.mycp import generateLoginTokenForURL, generateOAuthTokenFromCredentials, setUserType, deleteLoginFile
from chilitools.utilities.defaults import STAFF_TYPE

def changeBackofficeURL(app: dict) -> dict:
  app['url'] = backofficeURLInput()
  return app

def getConnector(app: dict) -> dict:
  if app['url'] is None:
    app = changeBackofficeURL(app)
  if 'connector' not in app.keys() or app['url'] != app['connector'].backofficeURL:
    app['connector'] = ChiliConnector(backofficeURL=app['url'])
  return app

def genLoginToken(app: dict, url: str = None) -> dict:
  if app['url'] is None and url is None:
    app = changeBackofficeURL(app)
  if url is None:
    url = app['url']
  token = generateLoginTokenForURL(backofficeURL=url)
  app['results'].append((url, token))
  return app

def getAPIKey(app: dict) -> dict:
  app = getConnector(app)
  app['results'].append((app['url'], app['connector'].getAPIKey()))
  return app

def deleteLogin(app: dict) -> dict:
  if deleteLoginFile():
    print("Successfully deleted login file")
  return app

def setCredentials(app: dict):
  app['results'].append(('OAuth Gen', generateOAuthTokenFromCredentials()))
  return app

def toggleCopy(app: dict) -> dict:
  if 'clipboard' in app.keys():
    app['clipboard'] = not app['clipboard']
  return app


def menuLoop(app: dict):
  while (True):

    # lastResult item is a tuple with the format (backofficeURL, function response)
    if len(app['results']) > 0:
      lastResult = app['results'][-1]
      if app['clipboard']:
        pc.copy(lastResult[1])
      print('\n' + lastResult[1] + '\n')

    menuItems = list(app['menuItems'].keys())
    print(f"CHILI Publish Testing Tools\t>>\tCopy Output: {app['clipboard']}")
    print("---------------------------------------------------------")

    for index, item in enumerate(menuItems):
      print(str(index + 1) + ') ' + item)

    if app['url'] is not None: print("Current Backoffice URL: " + app['url'])

    option = input()

    if 'staff' in option:
      print('Successfully enabled 2FA staff login for BackOffice')
      setUserType(userType=STAFF_TYPE)
      continue
    elif 'exit' in option:
      break

    try:
      option = int(option) - 1
      if option >= 0:
        func = app['menuItems'][menuItems[option]]
        # TODO create app['lastCommand'] and append that on the results tuple instead of the url. instead, add the url to the last command entry
        if isinstance(func, tuple):
          app = func[0](app, func[1])
        else:
          app = func(app)
    except Exception as e:
      print('\nThat is not a valid option, please try again')
      print(e)

def menu():
  app = {
    'clipboard': True,
    'url': None,
    'results': list(),
  }

  app['menuItems'] = {
    'Generate login token for BackOffice URL': genLoginToken,
    'Get API Key for BackOffice URL': getAPIKey,
    'Generate login token for ft-nostress': (genLoginToken, 'https://ft-nostress.chili-publish.online/ft-nostress/interface.aspx'),
    'Generate login token for ft-nostress-sandbox': (genLoginToken, 'https://ft-nostress.chili-publish-sandbox.online/ft-nostress/interface.aspx'),
    'Generate OAuth2 token': setCredentials,
    'Toggle copy output to clipboard': toggleCopy,
    'Change BackOffice URL': changeBackofficeURL,
    'Clear login credentials': deleteLogin,
  }
  menuLoop(app)