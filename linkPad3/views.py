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

	# get query string
	if request.args.get('q') != "" and request.args.get('q') != None:
		q = request.args.get('q')
	else:
		q = "*:*"

	# get current page
	if request.method == "GET" and request.args.get('page') != "":
		current_page = request.args.get('page')
	else:
		current_page = "1"

	solr_params = {
		"q":q,
		"start":0,
		"rows":localConfig.per_page,
		"sort":"last_modified desc"
	}
	search_results = solr_handle.search(**solr_params)

	# failed search
	if search_results.total_results == 0:
		return render_template("index.html",message="Sorry bud, nothing to report.")		

	# successful search
	else:
		pagination = models.Pagination(current_page, localConfig.per_page, search_results.total_results)
		return render_template("index.html",pagination=pagination,search_results=search_results)


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
			page_html = requests.get("http://localhost:8050/render.html?url={add_url}&wait=1".format(add_url=add_url)).content
			link.doc['int_fullText'] = page_html
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

		return str(update_response.raw_content)



	return "Not a normal pattern, try again."



@app.route("/delete", methods=['GET', 'POST'])
def delete():
	'''
	Remove link from Solr
	'''

	doc_id = request.args.get('id')		
	link = models.Link()
	link.getLink(doc_id)
	delete_response = link.delete()
	print delete_response.raw_content

	return redirect('./')






######################################################
# Catch all - DON'T REMOVE
######################################################
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):    
	return "<p>Cannot find that, dummy.  For your health!"













