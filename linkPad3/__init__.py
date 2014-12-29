# root file, app instantiator

# modules / packages import
from flask import Flask, render_template, g

from solrHandles import solr_handle
import redisHandles

# create app
app = Flask(__name__)

# get handlers
import views