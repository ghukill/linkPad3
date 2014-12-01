# -*- coding: utf-8 -*-

# library
from twisted.web.wsgi import WSGIResource
from twisted.web.server import Site
from twisted.internet import reactor, defer
from twisted.internet.task import deferLater
from twisted.web.server import NOT_DONE_YET
from twisted.web import server, resource
from twisted.python import log
import json
import logging 
import os

import localConfig

# import linkPad3 app
from linkPad3 import app

# twisted liseners
logging.basicConfig(level=logging.DEBUG)

# linkPad3
resource = WSGIResource(reactor, reactor.getThreadPool(), app)
site = Site(resource)

if __name__ == '__main__':

	# linkPad3
	print "Starting linkPad3..."
	reactor.listenTCP( localConfig.app_port, site)

	print '''               
██╗     ██╗███╗   ██╗██╗  ██╗██████╗  █████╗ ██████╗      ██████╗ 
██║     ██║████╗  ██║██║ ██╔╝██╔══██╗██╔══██╗██╔══██╗     ╚════██╗
██║     ██║██╔██╗ ██║█████╔╝ ██████╔╝███████║██║  ██║█████╗█████╔╝
██║     ██║██║╚██╗██║██╔═██╗ ██╔═══╝ ██╔══██║██║  ██║╚════╝╚═══██╗
███████╗██║██║ ╚████║██║  ██╗██║     ██║  ██║██████╔╝     ██████╔╝
╚══════╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝╚═════╝      ╚═════╝ 
                                                                  
	'''
	reactor.run()
