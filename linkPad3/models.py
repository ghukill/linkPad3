from math import ceil

# Solr
from solrHandles import solr_handle

class Pagination(object):

	def __init__(self, page, per_page, total_count):
		self.page = page
		self.per_page = per_page
		self.total_count = total_count

	@property
	def pages(self):
		return int(ceil(self.total_count / float(self.per_page)))

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
		

	def getLink(self,doc_id):
		self.id = doc_id

		solr_params = {
			"q":"id:{doc_id}".format(doc_id=doc_id),
			"start":0,
			"rows":1
		}
		search_results = solr_handle.search(**solr_params)
		doc = search_results.documents[0]
		self.doc = doc

	def update(self):
		update_respone = solr_handle.update([self.doc], commit=True)		
		return update_respone

	def delete(self):
		delete_response = solr_handle.delete_by_key(self.id, commit=True)
		return delete_response

	def indexHTML(self):
		pass

	def getThumb(self):
		pass