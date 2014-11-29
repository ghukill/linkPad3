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
from datetime import datetime

# flask proper
from flask import render_template, request, session, redirect, make_response, Response, Blueprint




# session data secret key
####################################
app.secret_key = 'linkPad3'
####################################



@app.route("/<current_page>")
def index(current_page):

	'''
	Create some kind of search class in models.py that accepts the pagination object
	'''

	solr_params = {
		"q":"python",
		"start":0,
		"rows":localConfig.per_page
	}
	search_results = solr_handle.search(**solr_params)

	pagination = models.Pagination(current_page, localConfig.per_page, search_results.total_results)

	return render_template("index.html",pagination=pagination,search_results=search_results)





######################################################
# Catch all - DON'T REMOVE
######################################################
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):    
	return "<p>Cannot find that, dummy.  For your health!"













