from os.path import dirname, realpath

path = dirname(realpath(__file__))

LOGIN_FILE = path+'/login.txt'
APIKEY_FILE = path+'/apiKeys.txt'
CONNECTOR_LOG_FILE = path+'./logs/ChiliConnector.log'