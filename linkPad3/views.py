# fm2
from linkPad3 import app

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

# flask proper
from flask import render_template, request, session, redirect, make_response, Response, Blueprint
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime

# get celery instance / handle
from cl.cl import celery

# Solr
from solrHandles import solr_handle

# session data secret key
####################################
app.secret_key = 'linkPad3'
####################################



@app.route("/")
def index():

	return "<p>Boom!</p>"






######################################################
# Catch all - DON'T REMOVE
######################################################
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):    
	return "<p>Cannot find that, dummy.  For your helath!"













