import re
import requests

from ..library import NotAuthenticatedError

class library:
    def __init__(self, url):
        """ Initialises the library. """
        
        self.session = requests.Session()
        self.authenticated = False;
        return
    
    def login(self, userid, password):
        """ Authenticates session for future use. """
        
        # find the "formdata" that we need to submit with the login
        r = self.session.get('https://rdg.ent.sirsidynix.net.uk/client/en_GB/main/search/patronlogin/')
        formdata = re.search('name="t:ac" type="hidden"></input><input value="(.*?)" name="t:formdata" type="hidden">', r.text).group(1)
        
        # log in
        postData = {
            'j_username': userid,
            'j_password': password,
            't:formdata': formdata }
        r = self.session.post('https://rdg.ent.sirsidynix.net.uk/client/en_GB/main/search/patronlogin.loginpageform/LIVE?&amp;t:ac=$N', postData)
        
        if "new RedirectAfterLogin('null');" in r.text:
            # if we get redirected, the login was successful!
            self.authenticated = True
            return True
        else:
            return False
    
    def search(self, query=None, title=None, author=None, ean=None):
        """ Performs a search, returning a (potentially empty) list of
        items. Optionally, search only within the title or author or 
        EAN / ISBN-13 attributes. """
        
        # perform the search        
        if query:
            result = self.session.get('https://rdg.ent.sirsidynix.net.uk/client/en_GB/main/search/results?qu=' + query)
        elif title:
            result = self.session.get('https://rdg.ent.sirsidynix.net.uk/client/en_GB/main/search/results?rt=false%7C%7C%7CTITLE%7C%7C%7CTitle&qu=' + title)
        elif author:
            result = self.session.get('https://rdg.ent.sirsidynix.net.uk/client/en_GB/main/search/results?rt=false%7C%7C%7CAUTHOR%7C%7C%7CAuthor&qu=' + author)
        elif ean:
            result = self.session.get('https://rdg.ent.sirsidynix.net.uk/client/en_GB/main/search/results?rt=false%7C%7C%7CISBN%7C%7C%7CISBN&qu=' + ean)
        else:
            raise ValueError
        
        results = []
        
        # interpret the results
        if 'Holds:' in result.text:
            # if we got to the page for a single item
            # item type, checks are orders so the most likely check to
            # pass is done first
            if '<div class="displayElementText GENRE_TERM"><a title="Electronic books" alt="Electronic books"' in result.text:
                # ebooks also have ISBN so we have to check this first
                itemtype = 'ebook'
            elif re.search('Loan Type.{0,350}?PERIODICAL', result.text, re.DOTALL):
                itemtype = 'journal'
            elif '<div class="displayElementText GENRE_TERM"><a title="Electronic journals." alt="Electronic journals."' in result.text:
                itemtype = 'ejournal'
            elif re.search('Call Number.{0,450}?THESIS(?: -|--)', result.text, re.DOTALL):
                # thesis
                itemtype = 'academic_paper'
            elif re.search('<div class="displayElementText TITLE">.{0,100}?\[cartographic material\]', result.text):
                # map / atlas
                itemtype = 'map'
            elif 'Electronic access:' in result.text:
                # electronic resources / cd-rom
                itemtype = 'electronic'
            elif re.search('<div class="displayElementText TITLE">.{0,100}?\[sound recording\]', result.text):
                # sound recording
                itemtype = 'audio'
            elif re.search('<div class="displayElementText TITLE">.{0,100}?\[videorecording\]', result.text):
                # dvd / video casette / visual materials
                itemtype = 'video'
            elif 'ISBN:' in result.text:
                # if it's nothing else and it has an ISBN it's probably a book
                itemtype = 'book'
            else:
                # archive, object, kit
                itemtype = 'other'
            # find an ID number to use
            identifier = None
            if itemtype == 'journal' or itemtype == 'ejournal':
                try:
                    identifier = re.search('<div class="displayElementText ISSN_LOCAL">(\d{4}-\d{4})', result.text).group(1)
                except AttributeError:
                    pass
            elif itemtype == 'academic_paper':
                identifier = re.search('Call Number.{0,4500}?THESIS(?: -|--|-)(R\d{0,6})', result.text, re.DOTALL).group(1)
            else:
                try:
                    identifier = re.search('<div class="displayElementText LOCAL_ISBN">(\d{13})', result.text).group(1)
                except AttributeError:
                    # no ISBN-13 / EAN recorded, drop to ISBN-10                
                    try:
                        identifier = re.search('<div class="displayElementText LOCAL_ISBN">(\d{10})', result.text).group(1)
                    except AttributeError:
                        pass
            if identifier == None: # if we couldn't find an ISBN / ISSN
                identifier = re.search("'ent://SD_ILS/\d{0,8}?/SD_ILS:(\d{0,10}?)'", result.text).group(1)
            # title
            fulltitle = re.search('<div class="displayElementText TITLE">(.*?)<\/div>', result.text).group(1)
            try:
                title = re.search('(.*?)(?: :| \/|\.)', fulltitle).group(1)
            except AttributeError:
                title = fulltitle # if the full title is also the normal title
            if ' / ' in fulltitle:
                # if the author has been embedded in the title use that
                # as it's generally more accurate
                author = re.search('.*? (?:\/ by|\/) (.*?)(?: ;|\.$|$)', fulltitle).group(1).split(', ')
            elif 'Personal author:' in result.text:
                # the personal author generally only includes the first
                # author, but it's the best we've got. it also sometimes
                # includes the years the author was alive, which is
                # annoying
                match = re.search('<div class="displayElementText PERSONAL_AUTHOR"><a title="(.*?), (.*?,|.*?\.).*?" alt=', result.text)
                first = match.group(2).rstrip(',')
                second = match.group(1)
                author = [first + ' ' + second]
            elif 'Added corporate author' in result.text:
                corporate_authors = "".join(re.findall('<div class="displayElementText ADDED_CORPORATE_AUTHOR">(.*?)</div>', result.text))
                author = re.findall('<a .*?>(.*?)</a>', corporate_authors)
            else:
                # not much else we can do other than return unknown
                author = ['unknown']
            results.append( {
                'id': identifier,
                'title': title,
                'author': author,
                'type': itemtype,
            } )
            
        elif 'results found' in result.text:
            # if we got to a page with lots of results
            number_of_results = re.search('(\d{0,7}?) results found', result.text).group(1)
            #if number_of_results > 120:
                # cap at 120 otherwise getting results could be slow
            #    number_of_results = 120
            print (result.text)
            while len(results) < int(number_of_results):
                types = re.findall('<div class="displayElementText highlightMe UR_FORMAT"> (.*?)</div>', result.text)
                for i in range(len(types)):
                    # title
                    fulltitle = re.search('<a id="detailLink' + str(i) + '" title="(.*?)"', result.text).group(1)
                    print (str(i))
                    print(fulltitle)
                    try:
                        title = re.search('(.*?)(?: :| \/|\.)', fulltitle).group(1)
                    except AttributeError:
                        pass # if the full title is also the normal title
                    if ' / ' in fulltitle:
                        # if the author has been embedded in the title use that
                        # as it's generally more accurate
                        author = re.search('.*? (?:\/ by|\/) (.*?)(?: ;|\.$|$)', fulltitle).group(1).split(', ')
                    else:
                        author = ['unknown']
                    
                    # type
                    if types[i] == 'Thesis':
                        itemtype = 'academic_paper'
                    elif types[i] == 'Sound disc':
                        itemtype = 'audio'
                    elif types[i] == 'Book':
                        if '[electronic resource]' in title:
                            itemtype = 'ebook'
                        else:
                            itemtype = 'book'
                    elif types[i] == 'Electronic Resources' or types[i] == 'CD-ROM':
                        itemtype = 'electronic'
                    elif types[i] == 'Journal':
                        if '[electronic resource]' in title:
                            itemtype = 'ejournal'
                        else:
                            itemtype = 'journal'
                    elif types[i] == 'Maps' or types[i] == 'Atlas':
                        itemtype = 'map'
                    elif types[i] == 'Printed music':
                        itemtype = 'audio'
                    elif types[i] == 'DVD' or types[i] == 'Video casette' or types[i] == 'Visual Materials':
                        itemtype = 'video'
                    else:
                        itemtype = 'other'
                    
                    # identifier
                    identifier = None
                    try:
                        identifier = re.search('<div id="hitlist' + str(i) + '_ISBN"><div class="ISBN_value">(\d{13})', result.text).group(1)
                    except AttributeError:
                        try:
                            identifier = re.search('<div id="hitlist' + str(i) + '_ISSN"><div class="ISSN_value">(\d\d\d\d-\d\d\d\d)', result.text).group(1)
                        except AttributeError:
                            pass
                    if identifier == None:
                        identifier = re.search('(\d{0,10})" type="hidden" id="da' + str(i) + '"', result.text).group(1)
                    
                    results.append( {
                        'id': identifier,
                        'title': title,
                        'author': author,
                        'type': itemtype,
                    } )
                    
                    if len(results) % 12 == 0: # we'll have run out of results, get more
                        if query:
                            result = self.session.get('https://rdg.ent.sirsidynix.net.uk/client/en_GB/main/search/results?qu=' + query + '&rw=' + str(len(results)))
                        elif title:
                            result = self.session.get('https://rdg.ent.sirsidynix.net.uk/client/en_GB/main/search/results?rt=false%7C%7C%7CTITLE%7C%7C%7CTitle&qu=' + title + '&rw=' + str(len(results)))
                        elif author:
                            result = self.session.get('https://rdg.ent.sirsidynix.net.uk/client/en_GB/main/search/results?rt=false%7C%7C%7CAUTHOR%7C%7C%7CAuthor&qu=' + author + '&rw=' + str(len(results)))
                        elif ean:
                            result = self.session.get('https://rdg.ent.sirsidynix.net.uk/client/en_GB/main/search/results?rt=false%7C%7C%7CISBN%7C%7C%7CISBN&qu=' + ean + '&rw=' + str(len(results)))
                        print (result.text)
                        
        return results
    
    def list_items(self):
        """ Returns a list of items the borrower has (currently formatted
        as a list of enterprise IDs). """
        if not self.authenticated:
            raise NotAuthenticatedError
        
        r = self.session.get('https://rdg.ent.sirsidynix.net.uk/client/en_GB/main/search/account?')
        
        # for some insane reason it's nessesary to get the holds to get an ID to get checkouts...
        r = self.session.post('https://rdg.ent.sirsidynix.net.uk/client/en_GB/main/search/account.holdsajax/true?', {'t:zoneid': 'holdsAjax'}, headers={'X-Requested-With': 'XMLHttpRequest'})
        zoneid = re.search("<div class='hidden t-zone' id='(.*?)'>", r.text).group(1)
        
        # request list of books checked out
        r = self.session.post('https://rdg.ent.sirsidynix.net.uk/client/en_GB/main/search/account.finesandcheckouts/-1/-1/$B/0/true?', {'t:zoneid': zoneid}, headers={'X-Requested-With': 'XMLHttpRequest'})
        books = re.findall('<span>([X\d]{10})<\\\/span>', r.text)
        return books
    
    def renew_all(self):
        r = self.session.get('https://rdg.ent.sirsidynix.net.uk/client/en_GB/main/search/account?')
        
        # for some insane reason it's nessesary to get the holds to get an ID to get checkouts...
        r = self.session.post('https://rdg.ent.sirsidynix.net.uk/client/en_GB/main/search/account.holdsajax/true?', {'t:zoneid': 'holdsAjax'}, headers={'X-Requested-With': 'XMLHttpRequest'})
        zoneid = re.search("<div class='hidden t-zone' id='(.*?)'>", r.text).group(1)
        
        # request list of books checked out
        r = self.session.post('https://rdg.ent.sirsidynix.net.uk/client/en_GB/main/search/account.finesandcheckouts/-1/-1/$B/0/true?', {'t:zoneid': zoneid}, headers={'X-Requested-With': 'XMLHttpRequest'})
        
        items = self.list_items()
        numberOfItems = len(items)

        formdata = re.search("<div class='t-invisible'><input value='(.*?)' name='t:formdata' type='hidden'>", r.text).group(1)
        listSubmitId = re.search("<input value='submit' class='hidden' id='(.*?)'", r.text).group(1)
        
        # renew items
        postData = {
            't:formdata': formdata,
            't:submit': '["' + listSubmitId + '[","myCheckouts_checkoutslist_submit"]',
            't:zoneid': 'checkoutItemsZone'}
        for i in range(numberOfItems):
            if i == 0: # special case
                postData['checkbox'] = 'on'
            else:
                postData['checkbox_' + str(i-1)] = 'on'
        r = self.session.post('https://rdg.ent.sirsidynix.net.uk/client/en_GB/main/search/account.checkouts.checkoutslist.form?pc=%7B%22checkoutsList%22%3A%22%22%7D', postData, headers={'X-Requested-With': 'XMLHttpRequest'})

        renewalStatus = {}
        for item in items:
            # check it renewed successfully
            if re.search(item + "<\\\/span><br/><span class='checkoutsRenewed'>Renewal succeeded.<\\\/span>", r.text):
                renewalStatus[item] = [True]
            else:
                renewalStatus[item] = [False]
            # fix this for "item recalled"
            dueDateMatch = re.search(item + ".*?class='checkoutsDueDate'>(\d\d)\/(\d\d)\/(\d\d)<\\\/td>", r.text)
            dueDate = '20' + dueDateMatch.group(3) + '-' + dueDateMatch.group(2) + '-' + dueDateMatch.group(1)
            renewalStatus[item].append(dueDate)

        return renewalStatus
