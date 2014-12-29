from math import ceil
import requests
import dateutil.parser

# Solr
from solrHandles import solr_handle

# Redis
from redisHandles import r_thumbs

# linkPad3 modules
import localConfig

class Pagination(object):

	def __init__(self, page, rows, total_results):
		self.page = page
		self.rows = rows
		self.total_results = total_results

	@property
	def pages(self):
		return int(ceil(self.total_results / float(self.rows)))

	@property
	def has_prev(self):
		# return T/F test
		return self.page > 1

	@property
	def has_next(self):
		# return T/F test
		return self.page < self.pages

	def iter_pages(self, left_edge=2, left_current=2,
				   right_current=5, right_edge=2):
		last = 0
		for num in xrange(1, self.pages + 1):
			if num <= left_edge or \
			   (num > self.page - left_current - 1 and \
				num < self.page + right_current) or \
			   num > self.pages - right_edge:
				if last + 1 != num:
					yield None
				yield num
				last = num


# model for handling individual links in LinkPad3
class Link(object):	

	def __init__(self):		
		self.id = False
		self.doc = {		
			"id": False,
			"linkTitle":False,
			"linkURL":False,
			"last_modified":"NOW",
			"int_fullText":False
		}
		self.thumb_binary = ''
		

	def getLink(self,doc_id):
		try:
			self.id = doc_id

			solr_params = {
				"q":"id:{doc_id}".format(doc_id=doc_id),
				"start":0,
				"rows":1
			}
			search_results = solr_handle.search(**solr_params)
			doc = search_results.documents[0]
			self.doc = doc
			self.date_parsed = dateutil.parser.parse(self.doc['last_modified'])
		except:
			return False

	def update(self):
		update_respone = solr_handle.update([self.doc], commit=True)		
		return update_respone

	def delete(self):
		delete_response = solr_handle.delete_by_key(self.id, commit=True)
		return delete_response

	def indexHTML(self):
		try:
			page_html = requests.get("http://162.243.93.130:8050/render.html?url={add_url}&wait=1".format(add_url=self.doc['linkURL'])).content
			self.doc['int_fullText'] = page_html
			print "HTML indexed."
			return True
		except:
			print "Could not generate full-text HTML of page."
			return False

	def getThumb(self):
		try:
			page_png_binary = requests.get("http://162.243.93.130:8050/render.png?url={add_url}&wait=1&width=320&height=240".format(add_url=self.doc['linkURL'])).content
			self.thumb_binary = page_png_binary
			r_thumbs.set(self.id,self.thumb_binary)
			print "Thumbnail binary retrieved."
			return True
		except:
			print "Could not generate page thumbnail."
			return False

	def retrieveThumb(self):
		if r_thumbs.exists(self.id):
			return r_thumbs.get(self.id)
		else:
			# return empty page thumbnail
			return r_thumbs.get('no_thumb')


# Search Class
class Search(object):

	def __init__(self,q="*:*", sort="last_modified desc", rows=localConfig.rows, page=1):

		self.q = q
		self.sort = sort
		self.rows = rows
		self.page = page		


	@property
	def start(self):
		if self.page > 1:
			start = self.rows * (self.page - 1)
		else:
			start = 0
		return start


	@property
	def total_record_count(self):
		# get total record count from Solr DB
		return solr_handle.search(q="*:*",rows=0).total_results


	def search(self):
		solr_params = {
			"q":self.q,
			"rows":self.rows,
			"start":self.start,
			"sort":self.sort
		}
		return solr_handle.search(**solr_params)


