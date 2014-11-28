from mysolr import Solr
import requests

import localConfig

# set connection through requests
session = requests.Session()
solr_handle = Solr(localConfig.solr_URL, make_request=session)

