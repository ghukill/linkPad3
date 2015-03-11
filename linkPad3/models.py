import os
from math import ceil
import requests
import dateutil.parser
from bs4 import BeautifulSoup
import urllib2
import datetime
import md5
import time
import logging

# Solr
from solrHandles import solr_handle

# Redis
# from redisHandles import r_thumbs, r_HTML

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


	def linkAdd(self, add_url):
		
		try:

			try:
				# get page title
				soup = BeautifulSoup(urllib2.urlopen(add_url))
				page_title = soup.title.string
			except:
				logging.info('Could not grab title, defaulting to URL')
				page_title = add_url

			# instantiate mostly empty Link object
			# link = models.Link()

			# set id
			self.id = md5.new(add_url+str(int(time.time()))).hexdigest()

			# index in Solr		
			self.doc = {		
				"id": self.id,
				"linkTitle":page_title,
				"linkURL":add_url,
				"last_modified":"NOW",
				"int_fullText":False
			}
			update_response = self.update()
			logging.debug(update_response.raw_content)

			# grab full-text HTML to index in int_fullText	
			if self.indexHTML() == True:
				self.update()

			# generate thumbnail
			self.getThumb()

			return self.id	
			
		except:
			logging.info("Could not index link.")
			return False
		

	def getLink(self, doc_id):
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
		# delete from solr
		solr_delete = solr_handle.delete_by_key(self.id, commit=True)
		
		# delete thumb from filesystem
		try:
			filename = localConfig.imageSource+self.id+".png"
			os.system('rm {filename}'.format(filename=filename))			
			loggin.info("thumbnail removed.")
		except:
			logging.info("file not found or could not be removed")

		if solr_delete.status == 200:
			logging.info("link deleted from Solr.")
			return True

		else:
			logging.debug("Solr Delete: {msg}".format(msg=solr_delete.status))
			return False


	def indexHTML(self):
		try:
			page_html = requests.get("http://{splash_server}/render.html?url={add_url}&wait=1".format(splash_server=localConfig.splash_server, add_url=self.doc['linkURL'])).content
			self.doc['int_fullText'] = page_html
			self.doc['HTMLstring'] = page_html
			
			logging.info("HTML indexed.")
			return True
		except:
			logging.info("Could not generate full-text HTML of page.")
			return False

	def getThumb(self):
		
		try:
			page_png_binary = requests.get("http://{splash_server}/render.png?url={add_url}&wait=1&width=320&height=240".format(splash_server=localConfig.splash_server, add_url=self.doc['linkURL'])).content
			logging.debug("Length of binary data {msg}".format(msg=str(len(page_png_binary))))
			if len(page_png_binary) < 50:
				raise Exception("Image binary suspiciously small, using default noImage.")

			# write to file
			filename = localConfig.imageSource+self.id+".png"
			fhand = open(filename,'wb')
			fhand.write(page_png_binary)
			fhand.close()
			logging.info("Thumbnail binary retrieved.")
			return True
		
		except Exception as e:
			logging.debug(e)
			# use default icon
			no_image_binary = open("linkPad3/static/images/noImage.png",'rb').read()
			filename = localConfig.imageSource+self.id+".png"
			fhand = open(filename,'wb')
			fhand.write(no_image_binary)
			fhand.close()
			logging.info("NoImage Thumbnail binary used.")
			return False
		

	def retrieveThumb(self):
		if r_thumbs.exists(self.id):
			return r_thumbs.get(self.id)
		else:
			# return empty page thumbnail
			return r_thumbs.get('no_thumb')



# Search Class
class Search(object):

	def __init__(self,q="*:*", sort="last_modified desc", rows=localConfig.rows, page=1, fl=""):

		self.q = q
		self.sort = sort
		self.rows = rows
		self.page = page
		self.fl = fl


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
			"sort":self.sort,
			"fl":self.fl
		}
		return solr_handle.search(**solr_params)


