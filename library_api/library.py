import re
import requests

def library(url):
    enterprise = '<span class="sdCopyrightLink"><a shape="rect" \
                  title="SirsiDynix" \
                  href="http://www.sirsidynix.com">\
                  SirsiDynix</a></span> - Enterprise Version 4.3'
    
    r = requests.get(url)
    if(enterprise in r.text)

    
    else:
        raise Exception
    
    class library(base):
        pass
        
    return library
