# -*- coding: utf-8 -*-

"""
direct PAS
Python Application Services
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
https://www.direct-netware.de/redirect?pas;http;tasks

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
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
----------------------------------------------------------------------------
https://www.direct-netware.de/redirect?licenses;gpl
----------------------------------------------------------------------------
#echo(pasHttpTasksVersion)#
#echo(__FILEPATH__)#
"""

from math import ceil

from dNG.data.hookable_settings import HookableSettings
from dNG.data.http.translatable_error import TranslatableError
from dNG.data.tasks.database_task import DatabaseTask
from dNG.data.text.input_filter import InputFilter
from dNG.data.text.l10n import L10n
from dNG.data.xhtml.table.custom import Custom as CustomTable

from .module import Module

class Index(Module):
    """
Service for "m=tasks"

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas.http
:subpackage: tasks
:since:      v0.2.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
    """

    def execute_index(self):
        """
Action for "index"

:since: v0.2.00
        """

        if (self.request.is_dsd_set("tid")): self.execute_view()
        else: self.execute_list()
    #

    def execute_list(self):
        """
Action for "list"

:since: v0.2.00
        """

        page = InputFilter.filter_int(self.request.get_dsd("tpage", 1))

        L10n.init("pas_http_tasks")

        session = (self.request.get_session() if (self.request.is_supported("session")) else None)
        user_profile = (None if (session is None) else session.get_user_profile())

        if (user_profile is None or (not user_profile.is_type("ad"))): raise TranslatableError("core_access_denied", 403)

        tasks_count = DatabaseTask.get_list_count()

        hookable_settings = HookableSettings("dNG.pas.http.tasks.List.getLimit")
        limit = hookable_settings.get("pas_http_tasks_list_limit", 40)

        pages = (1 if (tasks_count == 0) else ceil(float(tasks_count) / limit))
        offset = (0 if (page < 1 or page > pages) else (page - 1) * limit)

        tasks_list = DatabaseTask.load_list(offset = offset, limit = limit)

        content = { "title": L10n.get("pas_http_tasks_database_entries_list"), "tasks_count": tasks_count }

        if (tasks_count > 0):
            details_renderer_attributes = { "type": CustomTable.COLUMN_RENDERER_CALLBACK_OSET,
                                            "callback": self._get_details_cell_content,
                                            "oset_template_name": "tasks.details_column",
                                            "oset_row_attributes": [ "id", "tid", "name", "hook", "time_updated" ]
                                          }

            status_renderer_attributes = { "type": CustomTable.COLUMN_RENDERER_CALLBACK_OSET,
                                           "callback": self._get_status_cell_content,
                                           "oset_template_name": "tasks.status_column",
                                           "oset_row_attributes": [ "status", "time_started", "timeout" ]
                                         }

            time_scheduled_renderer_attributes = { "type": CustomTable.COLUMN_RENDERER_OSET,
                                                   "oset_template_name": "tasks.time_scheduled_column"
                                                 }

            table = CustomTable()
            table.add_column("details", L10n.get("pas_http_tasks_entry_details"), 50, renderer = details_renderer_attributes)
            table.add_column("status", L10n.get("pas_http_tasks_entry_status"), 30, renderer = status_renderer_attributes)
            table.add_column("time_scheduled", L10n.get("pas_http_tasks_entry_time_scheduled"), 20, renderer = time_scheduled_renderer_attributes)

            table.set_limit(limit)
            table.set_row_count(tasks_count)

            for task in tasks_list:
                task_data = task.get_data_attributes("id",
                                                     "tid",
                                                     "name",
                                                     "status",
                                                     "hook",
                                                     "time_started",
                                                     "time_scheduled",
                                                     "time_updated",
                                                     "timeout"
                                                    )

                table.add_row(**task_data)
            #

            content['tasks'] = { "object": table,
                                 "dsd_page_key": "tpage",
                                 "page": page
                               }
        #

        self.response.init(True)
        self.response.set_expires_relative(+5)
        self.response.set_title(content['title'])

        self.response.add_oset_content("tasks.list", content)
    #

    def _get_details_cell_content(self, content, column_definition):
        """
Returns content used for the "details" cell rendering.

:param content: Content already defined
:param column_definition: Column definition for the cell

:return: (dict) Content used for rendering
:since:  v0.2.00
        """

        _return = content

        # @TODO: Code me
        # link_parameters = { "m": "tasks",
        #                    "a": "view",
        #                    "dsd": { "tid": content['id'] }
        #                  }

        #_return['link'] = Link().build_url(Link.TYPE_RELATIVE_URL, link_parameters)

        return _return
    #

    def _get_status_cell_content(self, content, column_definition):
        """
Returns content used for the "size" cell rendering.

:param content: Content already defined
:param column_definition: Column definition for the cell

:return: (dict) Content used for rendering
:since:  v0.2.00
        """

        _return = content

        if (content['status'] == DatabaseTask.STATUS_WAITING): _return['status'] = L10n.get("pas_http_tasks_entry_status_waiting")
        elif (content['status'] == DatabaseTask.STATUS_QUEUED): _return['status'] = L10n.get("pas_http_tasks_entry_status_queued")
        elif (content['status'] == DatabaseTask.STATUS_RUNNING): _return['status'] = L10n.get("pas_http_tasks_entry_status_running")
        elif (content['status'] == DatabaseTask.STATUS_COMPLETED): _return['status'] = L10n.get("pas_http_tasks_entry_status_completed")
        elif (content['status'] == DatabaseTask.STATUS_FAILED): _return['status'] = L10n.get("pas_http_tasks_entry_status_failed")
        else: _return['status'] = L10n.get("core_unknown_entity")

        if (content['time_started'] < 1): _return['time_started'] = None
        if (content['timeout'] < 1): _return['timeout'] = None

        return _return
    #
#
