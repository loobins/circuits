# Module:	__init__
# Date:		3rd October 2008
# Author:	James Mills, prologic at shortcircuit dot net dot au

"""Circuits Library - Web

circuits.lib.web contains the circuits full stack web server and wsgi library.

@deprecated: The wsgi Components will be going away in 1.2 in favour of just
             importing the wsgo module. Post 1.2 please use circutis.web.wsgi
"""

import wsgi
import tools
from loggers import Logger
from core import Controller
from sessions import Sessions
from events import Request, Response
from servers import BaseServer, Server
from errors import HTTPError, Forbidden, NotFound, Redirect
from dispatchers import Dispatcher, VirtualHosts, XMLRPC, JSONRPC
