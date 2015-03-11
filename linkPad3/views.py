# linkPad3
from linkPad3 import app
from linkPad3 import models

# get celery instance / handle
from cl.cl import celery

# Solr
from solrHandles import solr_handle

# from redisHandles import r_thumbs

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
import StringIO
import logging

# flask proper
from flask import render_template, request, session, redirect, make_response, Response, Blueprint, jsonify


# session data secret key
####################################
app.secret_key = 'linkPad3' ########
####################################


@app.route("/", methods=['GET', 'POST'])
def index():

	# instantiate Search object
	search_handle = models.Search()	

	# detect if search
	if request.args.get('q') != "" and request.args.get('q') != "*:*" and request.args.get('q') != None:
		search_handle.q = request.args.get('q')
		# search_handle.q.op = "AND" # how to do this without do notation?
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

	# catpure IP
	ip = request.remote_addr
	logging.debug(ip)

	# perform search
	search_handle.results = search_handle.search()

	# failed search
	if search_handle.results.total_results == 0:
		return render_template("index.html",search_handle=search_handle,message="Sorry pardner, none found.", ip=ip, urlprefix=localConfig.urlprefix)		

	# successful search
	else:
		pagination = models.Pagination(page=search_handle.page, rows=localConfig.rows, total_results=search_handle.results.total_results)
		return render_template("index.html",pagination=pagination,search_handle=search_handle, ip=ip, urlprefix=localConfig.urlprefix)


@app.route("/tiles", methods=['GET', 'POST'])
def tiles():

	# instantiate Search object
	search_handle = models.Search()	

	# bump tile num to 50
	search_handle.rows = 50

	# detect if search
	if request.args.get('q') != "" and request.args.get('q') != "*:*" and request.args.get('q') != None:
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
		return render_template("tiles.html",search_handle=search_handle,message="Sorry pardner, none found.")		

	# successful search
	else:
		pagination = models.Pagination(page=search_handle.page, rows=localConfig.rows, total_results=search_handle.results.total_results)
		return render_template("tiles.html",pagination=pagination,search_handle=search_handle)


# return archived HTML for link
@app.route("/archive/<id>", methods=['GET', 'POST'])
def archive(id):

	# open link handle
	link = models.Link()
	link.getLink(id)

	# return HTML
	return link.doc['HTMLstring']


@app.route("/add", methods=['GET', 'POST'])
def add():

	# get query string
	if request.args.get('url') != "" and request.args.get('url') != None:
		add_url = request.args.get('url')
	else:
		return redirect("/{urlprefix}/".format(urlprefix=localConfig.urlprefix))

	# celery task	
	# linkAdd.delay(add_url)

	# # normy task
	# link = models.Link()
	# doc_id = link.linkAdd(add_url)
	# if doc_id == False:
	# 	return "Could not index link."

	# return render_template("add.html",add_url=add_url,doc_id=doc_id)
	
	# push to /add_background as ajax
	return render_template("add.html", add_url=add_url, urlprefix=localConfig.urlprefix)



@app.route("/add_background", methods=['GET', 'POST'])
def add_background():

	# get query string
	if request.args.get('url') != "" and request.args.get('url') != None:
		add_url = request.args.get('url')
	else:
		return redirect("/{urlprefix}/".format(urlprefix=localConfig.urlprefix))

	# normy task	
	return_dict = {}
	link = models.Link()
	doc_id = link.linkAdd(add_url)
	if doc_id == False:
		return_dict['status'] = False
	else:
		return_dict['status'] = True
		return_dict['id'] = doc_id

	return jsonify(**return_dict)	


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

		return render_template("edit.html",doc=link.doc,urlprefix=localConfig.urlprefix)

	# commit changes
	if request.method == "POST":
		doc_id = request.form['id']		
		link = models.Link()
		link.getLink(doc_id)

		link.doc['linkTitle'] = request.form['linkTitle']
		link.doc['linkURL'] = request.form['linkURL']
		link.doc['comments'] = request.form['comments']
		update_response = link.update()		

		return redirect('/linkPad3/')



@app.route("/delete", methods=['GET', 'POST'])
def delete():
	'''
	Remove link from Solr
	'''
	doc_id = request.args.get('id')		
	link = models.Link()
	link.getLink(doc_id)
	delete_response = link.delete()
	return redirect('/{urlprefix}/'.format(urlprefix=localConfig.urlprefix))


# @app.route("/linkThumb", methods=['GET', 'POST'])
# def linkThumb():
	
# 	'''
# 	Return link thumbnail
# 	'''
# 	try:
# 		doc_id = request.args.get('id')
# 		# print "Looking for",doc_id
# 		link = models.Link()
# 		link.getLink(doc_id)

# 		# return image binary
# 		response = make_response(link.retrieveThumb())
# 		response.headers['Content-Type'] = 'image/png'
# 		# response.headers['Content-Disposition'] = 'attachment; filename=link_thumbnail.png'
# 		return response

# 	except:
# 		# return image binary
# 		response = make_response(r_thumbs.get('no_thumb'))
# 		response.headers['Content-Type'] = 'image/png'
# 		# response.headers['Content-Disposition'] = 'attachment; filename=link_thumbnail.png'
# 		return response








######################################################
# Catch all - DON'T REMOVE
######################################################
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):    
	return "<p>Cannot find that, dummy.  For your health!"













