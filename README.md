# chilitools


_NOTICE: This package is no longer under active development. It the result of my time working for CHILI Publish. No garuntees how well these items work. They are primarily made to work with Publisher which has a pretty stabalized API so most of the items should still work with minimal modification._

chilitools is a python package useful for interacting with products from [CHILI publish](https://www.chili-publish.com/). There are many tools in this package for interacting with documents, endpoints, and for debugging.

The package is located on [PyPi](https://pypi.org/project/chilitools/) index so you can download it using pip
```sh
pip install chilitools
```

To install the dependencies from the pyproject file and run from this repo (recommended) you will need Poetry and to run
```sh
poetry install
```

Most of this library was written adhoc with little formal planning. This means that the library is very opinionated and sometimes the opinions even conflict (like jumping for camelCase names to the more pythonic snake_case). Most REST API endpoints are covered, but not all.


##### The toolset
- [ChiliConnector (Publisher)](#chiliconnector)
- [Useful CHILI functions](#useful-chili-functions)
- [A premade easy to use logger *with colors*](#logger)
- [ServerMigrator](#servermigrator)
---


### ChiliConnector

First we will quickly talk about authentication. You have two methods for authentication for ChiliConnector. You can adhoc define credentials when initiating the class, or you can set environment variables on your system that will get pulled.

Example:
```python
from chilitools.api.connector import ChiliConnector

chili = ChiliConnector(
    backofficeURL='https://ft-nostress.chili-publish-sandbox.online/ft-nostress/interface.aspx',
    username="BackOffice username",
    password="BackOffice password")
```
If you are a CHILI staff member there is a botox wrapper to automatically generate credentials for any Publisher environment. This is the easiest method to authenticate and the recommended method. To do this you simply set these environment variables on your machine.
```sh
export CHILI_PUBLISH_USERNAME="<YOUR BOTOX/AD USERNAME>"
export CHILI_PUBLISH_PASSWORD="<YOUR AD PASSWORD>"
```

Now when you create a ChiliConnector all you need is the BackOffice URL
```python
from chilitools.api.connector import ChiliConnector

chili = ChiliConnector('https://ft-nostress.chili-publish-sandbox.online/ft-nostress/interface.aspx')
```

API keys are generated as needed automatically once you setup one of the authentication methods above. API stored in a JSON file in the package files. Their expiration date is checked before every request and they are re-generated if needed. If you ever need to get an API directory from a ChiliConnector you can just use this function
chili.


**Using Endpoints**
The most basic usage of a ChiliConnector is to interact with the REST API endpoints of a Publisher environment. This can be done with these attributes of the ChiliConnector object. Most endpoints are here, if they are not, you can technically make any request with the "makeRequest" function attribute on the ChiliConnector object. If the 'authRequired' boolean is set to true it will attach an API kep to the request you need.

`chili.resources.`
`chili.system.`
`chili.documents.`

These endpoint functions technically return a "ChiliResponse" object, if I had to write this again I would probably not do that, it primarily was to deal with converting XML responses to JSON/python dictionary objects seamlessly. I would probably take the time to serialize for "pythonic simplicity" sakes, but the two primary things you can check is ChiliResponse.success to see if the response was a success code,

_Example Workflow_
```python
resp = chili.resources.ResourceItemGetXML(
    resourceType="documents",
    itemID="ee1d3337-3404-4f3e-829b-102edde77098"
)

if not resp.success:
    print(f"The request failed: {resp.text}")

doc_xml = resp.text
```
_I typically log my non-success errors with the [logger](#logger) included in this package that you can pass to the ChiliConnector_

### Useful CHILI functions
There is a handful of useful functions in the package made for various CHILI bugs/workarounds or processes needed for an integration. Here are some of them with examples below.

**Generate and download PDF**
This `generateAndDownloadPDF` function takes a ChiliConnector, a path for the output file, then either a documentID or documentXML plus a settingsID or SettingsXML. This make it easy to test document generations on the fly.

This function also uses an internal function on the ChiliConnector.system endpoints called `waitForTask` that will wait on a CHILI task to finish. The return type of this function is a string indicating the resulting status of the function. This is a result of my playing with various programming styles.

```python
from chilitools.api.connector import ChiliConnector
from chilitools.utilities.file import generateAndDownloadPDF

chili = ChiliConnector('https://ft-nostress.chili-publish-sandbox.online/ft-nostress/interface.aspx')

print(generateAndDownloadPDF(
    connector=chili,
    fullFileName="output.pdf",
    documentID="aa304231-1a53-40da-90cb-1fc8f4808200",
    settingsID="14422a2a-1362-49b3-adfe-e8a4170078df"
))
```

**Get a flat list of all items under a directory**
There are two useful "recursive" functions that will traverse the directory tree of a resource. One will return a dict of all the <item> nodes included in the treelevel responses.

```python
chili.resources.getFullResourceTree(
    resourceType="documents",
)
```

You can also optionally specify a `folder` (bad naming I know) argument to get the full resource tree starting from a base path.

The more useful version I have for easily gathering all the item id's under a resource directory is get_items_in_tree

```python
chili.resources.get_items_in_tree(
    resourceType="documents"
)
```

This will simply just return a python list of all item ids. This also takes an optional `folder` argument to start from a base path.

**Restore Files / Add files to env**

(The closest thing I know to a restore tool)

There is a tool that will essentially upload the directory structure and documents in each directory. It will set the ID for the documents based on the id in the document XML.

You can find the script in [scripts/addDocsRecursive.py](/scripts/AddDoc/addDocsRecurisve.py). There is also a more basic manual addDocs.py but that one is not as cool.

You simply put your document XML files+folders in the "docs" folder and then modify the addDocsRecursive script and change the backoffice URL to the backoffice you want to upload the documents to. (removeTimeline will remove any <timeline> nodes in the documents, it was an old thing to clean up documents with the bug) and the base_path to specify the base path directory of uploading the documents + folder structure inside the "docs" folder.



**Base64 string of file byte stream**
_I also use pyperclip to put it in my clipboard, useful for working with swagger, but you can also just use the b64 string in requests with this library as well_
```python
import pyperclip as pc
from chilitools.utilities.file import getBase64String

b64 = getBase64String("chainsaw-butterfly.png")
pc.copy(b64)
```

### Logger
There is an easy to use logger included in this library. It will create a log file at the file path you specify when
creating it. This logger will print to your terminal (stdout) and to the file you specified. It has also has pretty colors which is what every logger needs.

The logger uses this date format because I am a filthy American: `08/23/2022 02:25:24 PM`
You can change this if you really want in the source of your local package install.
The source code is located in [utilities/logger.py](/chilitools/utilities/logger.py)

**Using it**
The logger requires a FULL file path (extensions are a construct for meer mortals, choose yours wisely) for the output log file. I like to get the path of where my script file is at and then base the log file path from that. This can be done using pythons "file" dunder attribute.

Your primary methods will be
`logger.info()` to print an info message
`logger.error()` to print a red error info message

```python
import os
from chilitools.utilities.logger import getLogger

current_dir = os.path.realpath(os.path.dirname(__file__)) + os.path.sep
logfile_path = current_dir + "big-chicken-wings23.log"

logger = getLogger(logfile_path)
logger.info(f"The log file is located at: {logfile_path}")
```

**Passing it to the ChiliConnector**
You can pass the logger to a ChiliConnector simply by specifying it and the ChiliConnector will log certain aspects. I did not get around to it fully logging at requests automatically. It is best if you do this in your own script workflows using the toolset

```python
chili = ChiliConnector(
    backofficeURL="backoffice url",
    username=username,
    password=password,
    logger=logger
)
```

### ServerMigrator
The all powerful server migrator is a result of ChiliConnector. This is a wrapper to facilitate the transfer of resource items from one environment to another via API calls. At one point it was used to merge two online environments. It handle (although buggy sometimes) document transfers and will detect and transfer any DataSources, Dynamic Asset Providers, Barcode Settings, and Assets within the document. Un-officially making it CHILI Publisher Packages 2.0.

The source file is located at in [utilities/ServerMigration.py](/chilitools/utilities/ServerMigration.py).

It requires a directory to store transfer metadata and the logs will be stored in this directory.

Below is a basic example establishing a ServerMigrator object between two environments. _Please note that if you are a CHILI admin and defined your email+password in your environment variables as mentioned in [ChiliConnector](#chiliconnector) you do not need to provide the username and password for each connector, but you can.

```python
from chilitools.api.connector import ChiliConnector
from chilitools.utilities.ServerMigration import ServerMigrator

source = ChiliConnector(
    backofficeURL="https://ft-nostress.chili-publish-sandbox.online/ft-nostress/interface.aspx",
    username="username",
    password="password"
)

dest = ChiliConnector(
    backofficeURL="https://ft-nostress.chili-publish.online/ft-nostress/interface.aspx",
    username="username",
    password="password"
)

sm = ServerMigrator(
    srcChili=source,
    destChili=dest,
    directory="transfer-logs"
)
```

Now that the ServerMigrator object is created, there are a couple options for transferring items. The most basic is to transfer a list of resource id's.

```python
sm.transferList(
    resource="documents",
    itemList=['docid1', 'docid2', 'docid3']
)
```

This will simply transfer all the items of a resource with the id's from the source environment to the destination environment. (This will preserve item IDs). Checks are performed to make sure duplicated are not added. Fonts + Assets file sizes are checked for truncation since that occasionally happens. Document going blank issue from being added is checked and avoided with DocumentProcessServerSide.

The other useful functions are `transferResource` and `transferAll`, To transfer a resource like documents, assets, users from one environment to another you can specify that.

```python
sm.transferResource(
    resource="documents",
    parentFolder="",
    customPath=""
)
```

Please note that `parentFolder` and `customPath` are optional. Essentially parentFolder allows you to specify a subfolder in the source environment to get all resource items under and transfer. customPath allows you to upload all the specific items under a custom path at the destination environment. Please note that customPath will still keep the directory structure in tact at the destination environment. All items won't be in that single folder.

`transferAll` is the GigaChad transfer tool that will transfer all environment resources from the source environment to the destination environment. This one has not been tested in some time and could need fixed.

```python
sm.transferAll()
```
