# -*- coding: utf-8 -*-
##j## BOF

"""
dNG.pas.plugins.http.tasks
"""
"""n// NOTE
----------------------------------------------------------------------------
direct PAS
Python Application Services
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
http://www.direct-netware.de/redirect.py?pas;http;tasks

The following license agreement remains valid unless any additions or
changes are being made by direct Netware Group in a written form.

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 2 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
more details.

You should have received a copy of the GNU General Public License along with
this program; if not, write to the Free Software Foundation, Inc.,
59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
----------------------------------------------------------------------------
http://www.direct-netware.de/redirect.py?licenses;gpl
----------------------------------------------------------------------------
#echo(pasHttpTasksVersion)#
#echo(__FILEPATH__)#
----------------------------------------------------------------------------
NOTE_END //n"""

from dNG.pas.controller.predefined_http_request import PredefinedHttpRequest
from dNG.pas.data.http.virtual_config import VirtualConfig
from dNG.pas.data.logging.log_line import LogLine
from dNG.pas.plugins.hooks import Hooks

def plugin_http_startup(params, last_return):
#
	"""
Called for "dNG.pas.http.startup" and "dNG.pas.http.wsgi.startup"

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:since:  v0.1.00
	"""

	VirtualConfig.set_virtual_path("/tasks/", { "uri": "tid", "uri_prefix": "/tasks/" }, plugin_handle_http_request)
	return last_return
#

def plugin_handle_http_request(request, virtual_config):
#
	"""
Called for requests with the path prefix "/tasks/".

:param request: Originating request instance
:param virtual_config: Virtual path configuration

:return: (object) Request object if valid
:since:  v0.1.00
	"""

	tid = request.get_dsd("tid")
	var_return = (None if (tid == None) else Hooks.call("dNG.pas.tasks.call", client = request.get_client_host(), tid = tid))

	if (var_return == None):
	#
		LogLine.warning("pas.tasks refused TID '{0}'".format(tid))

		var_return = PredefinedHttpRequest()
		var_return.set_module("output")
		var_return.set_service("http")
		var_return.set_action("error")
		var_return.set_dsd("code", "400")
	#

	return var_return
#

def plugin_deregistration():
#
	"""
Unregister plugin hooks.

:since: v0.1.00
	"""

	Hooks.unregister("dNG.pas.http.startup", plugin_http_startup)
	Hooks.unregister("dNG.pas.http.wsgi.startup", plugin_http_startup)
#

def plugin_registration():
#
	"""
Register plugin hooks.

:since: v0.1.00
	"""

	Hooks.register("dNG.pas.http.startup", plugin_http_startup)
	Hooks.register("dNG.pas.http.wsgi.startup", plugin_http_startup)
#

##j## EOF