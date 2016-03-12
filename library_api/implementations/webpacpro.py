import re
import requests
from bs4 import BeautifulSoup

class library:
	def __init__(self):
		self.session = requests.Session()

		return

	def login(self, userid, password):
		postData = {
			'extpatid': username,
			'extpatpw': password
		}

		res = self.session.post('https://library.aston.ac.uk/patroninfo', postData)

		return

	def search(self, query=None, title=None, author=None):
		results = []

		if not (query or title or author):
			raise ValueError
		elif query:
			res = self.session.get('https://library.aston.ac.uk/search~S9/?searchtype=X&searcharg=' + query)
		elif title:
			res = self.session.get('https://library.aston.ac.uk/search~S9/?searchtype=t&searcharg=' + title)
		elif author:
			res = self.session.get('https://library.aston.ac.uk/search~S9/?searchtype=t&searcharg=' + author)

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
		print(res.text)
		return

class _library:
	def list_items(session):
		return

	def list_reservations(session):
		return

	def renew(session, id):
		return

	def renew_all(session):
		return
