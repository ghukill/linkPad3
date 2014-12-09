# linkPad3
from linkPad3 import app
from linkPad3 import models

# get celery instance / handle
from cl.cl import celery

# Solr
from solrHandles import solr_handle

# localConfig
import localConfig

# python modules
import time
import json
import pickle
import sys
from uuid import uuid4
import json
import unicodedata
import shlex, subprocess
import socket
import hashlib
import os
from bs4 import BeautifulSoup
import urllib2
import datetime
import md5
import requests

# flask proper
from flask import render_template, request, session, redirect, make_response, Response, Blueprint

# session data secret key
####################################
app.secret_key = 'linkPad3'
####################################


@app.route("/", methods=['GET', 'POST'])
def index():

	# instantiate Search object
	search_handle = models.Search()	

	# detect if search
	if request.args.get('q') != "" and request.args.get('q') != None:
		search_handle.q = request.args.get('q')
		search_handle.sort = ""
	else:
		search_handle.q = "*:*"
		search_handle.sort = "last_modified desc"

	# choose sort type
	if request.args.get('sort') != "" and request.args.get('sort') != None:
		search_handle.sort = request.args.get('sort')	

	# get current page
	if request.args.get('page') != "" and request.args.get('page') != None:
		search_handle.page = int(request.args.get('page'))
	else:
		search_handle.page = 1

	# perform search
	search_handle.results = search_handle.search()

	# failed search
	if search_handle.results.total_results == 0:
		return render_template("index.html",search_handle=search_handle,message="Sorry pardner, none found.")		

	# successful search
	else:
		pagination = models.Pagination(page=search_handle.page, rows=localConfig.rows, total_results=search_handle.results.total_results)
		return render_template("index.html",pagination=pagination,search_handle=search_handle)


@app.route("/add", methods=['GET', 'POST'])
def add():

	# get query string
	if request.args.get('url') != "" and request.args.get('url') != None:
		add_url = request.args.get('url')
	else:
		return redirect("./")

	linkAdd.delay(add_url)

	# future solr id
	doc_id = md5.new(add_url).hexdigest()

	return render_template("add.html",add_url=add_url,doc_id=doc_id)


@celery.task(name="linkAdd")
def linkAdd(add_url):
	
	try:
		# get page title
		soup = BeautifulSoup(urllib2.urlopen(add_url))
		page_title = soup.title.string

		# index in Solr
		link = models.Link()
		link.doc = {		
			"id": md5.new(add_url).hexdigest(),
			"linkTitle":page_title,
			"linkURL":add_url,
			"last_modified":"NOW",
			"int_fullText":False
		}
		update_response = link.update()

		# grab full-text HTML to index in int_fullText	
		try:
			link.indexHTML()
			link.update()
		except:
			print "Could not render page, skipping full HTML"		
		
		print update_response.raw_content	
		
	except:
		"Could not index link."



@app.route("/edit", methods=['GET', 'POST'])
def edit():
	'''
	Retrieve solr document, render to page, edit, update.
	'''

	# prepare to edit
	if request.method == "GET":
		doc_id = request.args.get('id')		
		link = models.Link()
		link.getLink(doc_id)

		return render_template("edit.html",doc=link.doc)

	# commit changes
	if request.method == "POST":
		doc_id = request.form['id']		
		link = models.Link()
		link.getLink(doc_id)

		link.doc['linkTitle'] = request.form['linkTitle']
		link.doc['linkURL'] = request.form['linkURL']
		update_response = link.update()		

		return redirect('./')



@app.route("/delete", methods=['GET', 'POST'])
def delete():
	'''
	Remove link from Solr
	'''

	doc_id = request.args.get('id')		
	link = models.Link()
	link.getLink(doc_id)
	delete_response = link.delete()
	print "link deleted."
	return redirect('./')






######################################################
# Catch all - DON'T REMOVE
######################################################
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):    
	return "<p>Cannot find that, dummy.  For your health!"













