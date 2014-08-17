# -*- coding: utf-8 -*-
##j## BOF

"""
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
"""

# pylint: disable=unused-argument

from dNG.pas.controller.predefined_http_request import PredefinedHttpRequest
from dNG.pas.data.http.virtual_config import VirtualConfig
from dNG.pas.data.logging.log_line import LogLine
from dNG.pas.data.tasks.database import Database as DatabaseTasks
from dNG.pas.data.tasks.memory import Memory as MemoryTasks
from dNG.pas.plugins.hook import Hook
from dNG.pas.runtime.exception_log_trap import ExceptionLogTrap

def call_database_task(request, virtual_config):
#
	"""
Called for requests with the path prefix "/tasks.d/".

:param request: Originating request instance
:param virtual_config: Virtual path configuration

:return: (object) Request object if valid
:since:  v0.1.00
	"""

	_return = None

	tid = request.get_dsd("tid")

	with ExceptionLogTrap("pas_http_site"):
	#
		_return = (None
		           if (tid == None) else
		           DatabaseTasks.get_instance().call({ "client": request.get_client_host(), "tid": tid })
		          )
	#

	if (_return == None):
	#
		LogLine.warning("pas.Tasks.database_call refused TID '{0}'", tid, context = "pas_http_site")
		_return = handle_task_result_none()
	#

	return _return
#

def call_memory_task(request, virtual_config):
#
	"""
Called for requests with the path prefix "/tasks.m/".

:param request: Originating request instance
:param virtual_config: Virtual path configuration

:return: (object) Request object if valid
:since:  v0.1.00
	"""

	_return = None

	tid = request.get_dsd("tid")

	with ExceptionLogTrap("pas_http_site"):
	#
		_return = (None
		           if (tid == None) else
		           MemoryTasks.get_instance().call({ "client": request.get_client_host(), "tid": tid })
		          )
	#

	if (_return == None):
	#
		LogLine.warning("pas.Tasks.memory_call refused TID '{0}'", tid, context = "pas_http_site")
		_return = handle_task_result_none()
	#

	return _return
#

def call_task(request, virtual_config):
#
	"""
Called for requests with the path prefix "/tasks/".

:param request: Originating request instance
:param virtual_config: Virtual path configuration

:return: (object) Request object if valid
:since:  v0.1.00
	"""

	_return = None

	tid = request.get_dsd("tid")

	with ExceptionLogTrap("pas_http_site"):
	#
		_return = (None
		           if (tid == None) else
		           Hook.call("dNG.pas.Tasks.call", client = request.get_client_host(), tid = tid)
		          )
	#

	if (_return == None):
	#
		LogLine.warning("pas.Tasks.call refused TID '{0}'", tid, context = "pas_http_site")
		_return = handle_task_result_none()
	#

	return _return
#

def handle_task_result_none():
#
	"""
Returns an HTTP 400 error request if no task matched.

:return: (object) Request object
:since:  v0.1.00
	"""

	_return = PredefinedHttpRequest()
	_return.set_module("output")
	_return.set_service("http")
	_return.set_action("error")
	_return.set_dsd("code", "400")

	return _return
#

def register_plugin():
#
	"""
Register plugin hooks.

:since: v0.1.00
	"""

	Hook.register("dNG.pas.http.Server.onStartup", on_startup)
	Hook.register("dNG.pas.http.Wsgi.onStartup", on_startup)
#

def on_startup(params, last_return = None):
#
	"""
Called for "dNG.pas.http.Server.onStartup" and "dNG.pas.http.Wsgi.onStartup"

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:return: (mixed) Return value
:since:  v0.1.00
	"""

	VirtualConfig.set_virtual_path("/tasks/", { "path": "tid" }, call_task)
	VirtualConfig.set_virtual_path("/tasks.d/", { "path": "tid" }, call_database_task)
	VirtualConfig.set_virtual_path("/tasks.m/", { "path": "tid" }, call_memory_task)
	return last_return
#

def unregister_plugin():
#
	"""
Unregister plugin hooks.

:since: v0.1.00
	"""

	Hook.unregister("dNG.pas.http.Server.onStartup", on_startup)
	Hook.unregister("dNG.pas.http.Wsgi.onStartup", on_startup)
#

##j## EOF