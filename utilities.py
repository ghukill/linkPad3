#utilities
import linkPad3
import time


def makeAllThumbs():
	all = linkPad3.solr_handle.search(q="*:*",rows=2000,start=0,sort="last_modified desc")
	count = 1

	for each in all.documents:
		print "Working on",count
		try:
			link_handle = linkPad3.models.Link()
			link_handle.getLink(each['id'])
			print link_handle.doc['linkTitle'],link_handle.doc['id']
			result = link_handle.getThumb()
			if result == False:
				time.sleep(5) # waits for splash_server to restart
		except:
			print "errors were had, skipping."
			time.sleep(5) # waits for splash_server to restart
		count += 1

	print "finis!"


def indexAllHTML():
	all = linkPad3.solr_handle.search(q="*:*",rows=10000)
	count = 1

	for each in all.documents:
		print "Working on",count
		try:
			link_handle = linkPad3.models.Link()
			link_handle.getLink(each['id'])
			print link_handle.doc['linkTitle']
			link_handle.indexHTML()
			link_handle.update()
		except:
			print "errors were had, skipping."
		count += 1

	print "finis!"