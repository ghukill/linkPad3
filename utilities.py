#utilities
import linkPad3
import time


def makeAllThumbs(iter_rows, iter_page):
	# all = linkPad3.solr_handle.search(q="*:*",rows=3000,start=0,sort="last_modified desc")
	# count = 1

	# for each in all.documents:
	# 	print "Working on",count
	# 	try:
	# 		link_handle = linkPad3.models.Link()
	# 		link_handle.getLink(each['id'])
	# 		print link_handle.doc['linkTitle'],link_handle.doc['id']
	# 		result = link_handle.getThumb()
	# 		if result == False:
	# 			time.sleep(5) # waits for splash_server to restart
	# 	except:
	# 		print "errors were had, skipping."
	# 		time.sleep(5) # waits for splash_server to restart
	# 	count += 1

	# print "finis!"

	total_count = linkPad3.models.Search()
	total_count = total_count.total_record_count
	pages = total_count / iter_rows
	print "Pages",pages

	for page in range(1,pages):
		if page < iter_page:
			continue
		print "Working on set:",page
		shand = linkPad3.models.Search(fl="id", rows=iter_rows, page=page).search()

		# iterate through chunk
		for doc in shand.documents:
			try:
				link_handle = linkPad3.models.Link()
				link_handle.getLink(doc['id'])
				print link_handle.doc['linkTitle'],link_handle.doc['id']
				result = link_handle.getThumb()
				if result == False:
					time.sleep(5) # waits for splash_server to restart
			except:
				print "errors were had, skipping."
				time.sleep(5) # waits for splash_server to restart




def indexAllHTML():
	all = linkPad3.solr_handle.search(q="*:*",sort="last_modified desc",rows=10000)
	count = 1

	for each in all.documents:
		print "Working on",count
		try:
			link_handle = linkPad3.models.Link()
			link_handle.getLink(each['id'])
			print link_handle.doc['linkTitle']
			index_result = link_handle.indexHTML()
			link_handle.update()			
			if index_result == False:
				raw_input("Hit enter to continue...")
		except:
			print "errors were had, skipping."
		count += 1

	print "finis!"
