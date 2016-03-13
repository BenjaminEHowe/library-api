import re
import requests

class NotAuthenticatedError(Exception):
    pass

def library(url):
    enterprise = ('<span class="sdCopyrightLink"><a shape="rect" '
                  'title="SirsiDynix" href="http://www.sirsidynix.com">'
                  'SirsiDynix</a></span>\n-\xa0Enterprise')
    exlibrisprimo = 'Powered by ExLibris Primo'
    webpacpro = 'WebPAC PRO &copy; Innovative Interfaces, Inc.'
    
    r = requests.get(url)
    if enterprise in r.text:
        from library_api.implementations.enterprise import library
    elif exlibrisprimo in r.text:
        from library_api.implementations.exlibrisprimo import library
    elif webpacpro in r.text:
        from library_api.implementations.webpacpro import library
    else:
        raise NotImplementedError
    
    library_object = library(url)
    
    return library_object
