##
#     Project: gCentralAccess
# Description: Manage external resources from a centralized management console
#      Author: Fabio Castelli (Muflone) <muflone@vbsimple.net>
#   Copyright: 2015-2016 Fabio Castelli
#     License: GPL-2+
#  This program is free software; you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the Free
#  Software Foundation; either version 2 of the License, or (at your option)
#  any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT
#  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
#  more details.
#  You should have received a copy of the GNU General Public License along
#  with this program; if not, write to the Free Software Foundation, Inc.,
#  51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA
##

import time

from gi.repository import Gtk

from gcentralaccess.models.abstract import ModelAbstract

processes = {}


class ModelProcesses(ModelAbstract):
    COL_TIMESTAMP = 1
    COL_HOST = 2
    COL_DESTINATION = 3
    COL_SERVICE = 4
    COL_DESCRIPTION = 5
    COL_PID = 6
    COL_ICON = 7

    def __init__(self, model):
        super(self.__class__, self).__init__(model)
        self.theme = Gtk.IconTheme.get_default()

    def add_data(self, item):
        """Add a new row to the model"""
        super(self.__class__, self).add_data(item)
        # Get the max id
        if len(self.model):
            new_id = int(self.model[len(self.model) - 1][self.COL_KEY]) + 1
        else:
            new_id = 1
        # Add a new row
        new_row = self.model.append(None, (
            str(new_id),
            self.get_current_timestamp(),
            item.host_name,
            item.destination_name,
            item.service_name,
            item.status,
            str(item.pid),
            None))
        self.rows[str(new_id)] = new_row
        return new_row

    def add_detail(self, treeiter, status, icon):
        """Add a detail row under the TreeIter"""
        new_row = self.model.append(treeiter, (None,
                                               self.get_current_timestamp(),
                                               None,
                                               None,
                                               None,
                                               status,
                                               None,
                                               None))
        # Update information on the TreeIter row
        self.set_description(treeiter, status)
        self.set_icon(treeiter, self.get_pixbuf_from_icon_name(icon))
        return new_row

    def get_pixbuf_from_icon_name(self, icon):
        """Get a standard icon from theme"""
        return self.theme.load_icon(icon_name=icon,
                                    size=24,
                                    flags=Gtk.IconLookupFlags.USE_BUILTIN)

    def get_description(self, treeiter):
        """Get the description from a TreeIter"""
        return self.model[treeiter][self.COL_DESCRIPTION]

    def set_description(self, treeiter, status):
        """Set the description from a TreeIter"""
        self.model[treeiter][self.COL_DESCRIPTION] = status

    def get_pid(self, treeiter):
        """Get the PID from a TreeIter"""
        return int(self.model[treeiter][self.COL_PID])

    def set_icon(self, treeiter, icon):
        """Set the icon from a TreeIter"""
        self.model[treeiter][self.COL_ICON] = icon

    def get_current_timestamp(self):
        return time.strftime('%Y/%m/%d %H:%M:%S')
