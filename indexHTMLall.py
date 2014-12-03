import linkPad3

all = linkPad3.solr_handle.search(q="*:*",rows=2000)
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
