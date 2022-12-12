from chilitools.utilities.errors import ErrorHandler

def isValidBackofficeURL(backofficeURL: str) -> bool:
    try:
        backoffice = splitURL(url=backofficeURL)
        if backoffice[-1].lower() != 'interface.aspx':
            return False
        return True
    except:
        return False

def splitURL(url: str) -> dict:
    return url.strip().split('/')

def getBaseURL(backofficeURL: str) -> str:
    if isValidBackofficeURL(backofficeURL=backofficeURL):
        url = splitURL(url=backofficeURL)
        # Check for on-prem backoffice URL
        if len(url) != 5:
            # url[3] would be the IIS application folder for on-prem. ex: /CHILI/
            return url[0] + '//' + url[2] + '/'+ url[3] + '/'
        return url[0] + '//' + url[2] + '/'
    return ErrorHandler().getError('INVALIDBACKOFFICEURL')

def isPrem(backofficeURL: str) -> bool:
    url = splitURL(url=backofficeURL)
        # Check for on-prem backoffice URL
    if len(url) != 5: return True
    return False

def getEnviormentName(backofficeURL: str) -> str:
    if isValidBackofficeURL(backofficeURL=backofficeURL):
        url = splitURL(url=backofficeURL)
        # Check for on-prem backoffice URL
        if len(url) != 5:
            return url[4]
        else:
            return url[3]
    return ErrorHandler().getError('INVALIDBACKOFFICEURL')

def getRequestURL(backofficeURL: str, version: str = '1.2') -> str:
    if isValidBackofficeURL(backofficeURL=backofficeURL):
        baseURL = getBaseURL(backofficeURL=backofficeURL)
        return baseURL + f'rest-api/v{version}'
    return ErrorHandler().getError('INVALIDBACKOFFICEURL')

def backofficeURLInput(backofficeURL: str = None) -> str:
    if backofficeURL == None:
        backofficeURL = ""

    while isValidBackofficeURL(backofficeURL=backofficeURL) != True:
        print("Please enter the URL for the BackOffice you would like an API key for (URL should end with '/interface.aspx'): ")
        backofficeURL = input()
        if 'exit' in backofficeURL: exit()
    return backofficeURL