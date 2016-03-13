import re
import requests
from bs4 import BeautifulSoup

class library:
	def __init__(self, url):
		self.session = requests.Session()
		self.url = url

		return

	def login(self, userid, password):
		postData = {
			'extpatid': username,
			'extpatpw': password
		}

		res = self.session.post(self.url + '/patroninfo', postData)

		return

	def search(self, query=None, title=None, author=None):
		results = []

		if not (query or title or author):
			raise ValueError
		elif query:
			res = self.session.get(self.url + '/search~S9/?searchtype=X&searcharg=' + query)
		elif title:
			res = self.session.get(self.url + '/search~S9/?searchtype=t&searcharg=' + title)
		elif author:
			res = self.session.get(self.url + '/search~S9/?searchtype=t&searcharg=' + author)

		soup = BeautifulSoup(res.text, 'html.parser')
		for result_row in soup.find_all(class_='briefCitRow'):
			result = {
				'isbn': re.search('bookjacket\?recid=(.*)&amp;', str(result_row)).group(1),
				'title': result_row.find(class_='briefcitTitle').find('a').text,
				'author': re.search('<\/a><\/span>\n<br\/>\n(.*)<br/>', str(result_row)).group(1),
				'type': re.search('src="/screens/media_(.*).gif"', str(result_row)).group(1)
			}

			results.append(result)

		return results

	def get_item(self, id):
		res = self.session.get('http://library.aston.ac.uk/record=' + id)

		#print(res.text)

		soup = BeautifulSoup(res.text, 'html.parser')

		call_number = re.search('<td valign="top" width="20%"  class="bibInfoLabel">Class Number<\/td>\n<td class="bibInfoData">\n(.*)<\/td>', res.text)
		publisher = re.search('<td valign="top" width="20%"  class="bibInfoLabel">Publication Information<\/td>\n<td class="bibInfoData">\n<a href=".*\/browse">(.*)<\/a>', res.text)
		raw_copies = re.finditer('<tr  class="bibItemsEntry">\n\n<td width="27%" ><!-- field 1 -->&nbsp;(.*) \n<!-- field y --></td>\n<td width="35%" ><!-- field C -->&nbsp;<a href=".*">(.*)</a> <!-- field v --><!-- field # -->&nbsp;</td>\n<td width="18%" ><!-- field ! -->&nbsp;(.*)</td>\n<td width="20%" ><!-- field % -->&nbsp;(.*) </td></tr>', res.text)
		copies = []

		for copy in raw_copies:
			available = False
			due = None

			if copy.group(4) == 'AVAILABLE':
				available = True
			else:
				due = copy.group(4)

			copies.append({
				'location': copy.group(1),
				'type': copy.group(3),
				'available': available,
				'due': due
			})

		if call_number:
			call_number = call_number.group(1)
		else:
			call_number = None

		if publisher:
			publisher = publisher.group(1)
		else:
			publisher = None

		result = {
			'author': re.search('<td valign="top" width="20%"  class="bibInfoLabel">Author<\/td>\n<td class="bibInfoData">\n<a href=".*\/browse">(.*)<\/a>', res.text).group(1),
			'call_number': call_number,
			'copies': copies,
			'copies_available': 0,
			'copies_total': 0,
			'date_of_publication': '',
			'ean': '',
			'publisher': publisher,
			'title': re.search('<td valign="top" width="20%"  class="bibInfoLabel">Title<\/td>\n<td class="bibInfoData">\n<strong>(.*)<\/strong>', res.text).group(1),
			'type': ''
		}

		print(result)
		return result

class _library:
	def list_items(session):
		raise NotImplementedError
		return []

	def list_reservations(session):
		raise NotImplementedError
		return []

	def renew(session, id):
		raise NotImplementedError
		return false

	def renew_all(session):
		raise NotImplementedError
		return false
