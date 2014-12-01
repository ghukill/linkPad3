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

	# get page title
	soup = BeautifulSoup(urllib2.urlopen(add_url))
	page_title = soup.title.string	

	# set date (do we need?)
	# current_date = datetime.datetime.now().isoformat() + "Z"
	
	# index in Solr
	documents = [{		
		"id": md5.new(add_url).hexdigest(),
		"linkTitle":page_title,
		"linkURL":add_url,
		"last_modified":"NOW"
	}]
	update_response = solr_handle.update(documents, commit=True)
	print update_response.raw_content
	solr_handle.commit()

	return "Document added!"




######################################################
# Catch all - DON'T REMOVE
######################################################
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):    
	return "<p>Cannot find that, dummy.  For your health!"













