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

from gi.repository import GdkPixbuf

import gcentralaccess.preferences as preferences
from gcentralaccess.preferences import ICON_SIZE

from gcentralaccess.models.abstract import ModelAbstract
from gcentralaccess.models.service_info import ServiceInfo

services = {}


class ModelServices(ModelAbstract):
    COL_DESCRIPTION = 1
    COL_COMMAND = 2
    COL_TERMINAL = 3
    COL_ICON = 4
    COL_PIXBUF = 5

    def __init__(self, model):
        super(self.__class__, self).__init__(model)
        self.icon_size = preferences.preferences.get(ICON_SIZE)

    def add_data(self, item):
        """Add a new row to the model if it doesn't exists"""
        super(self.__class__, self).add_data(item)
        if item.name not in self.rows:
            icon = item.icon if item.icon is not None else ''
            pixbuf = None if icon == '' else \
                GdkPixbuf.Pixbuf.new_from_file_at_size(item.icon,
                                                       self.icon_size,
                                                       self.icon_size)
            new_row = self.model.append((
                item.name,
                item.description,
                item.command,
                item.terminal,
                icon,
                pixbuf))
            self.rows[item.name] = new_row
            return new_row

    def set_data(self, treeiter, item):
        """Update an existing TreeIter"""
        super(self.__class__, self).set_data(treeiter, item)
        icon = item.icon if item.icon is not None else ''
        pixbuf = None if icon == '' else \
            GdkPixbuf.Pixbuf.new_from_file_at_size(item.icon,
                                                   self.icon_size,
                                                   self.icon_size)
        self.model.set_value(treeiter, self.COL_KEY, item.name)
        self.model.set_value(treeiter, self.COL_DESCRIPTION, item.description)
        self.model.set_value(treeiter, self.COL_COMMAND, item.command)
        self.model.set_value(treeiter, self.COL_TERMINAL, item.terminal)
        self.model.set_value(treeiter, self.COL_ICON, icon)
        self.model.set_value(treeiter, self.COL_PIXBUF, pixbuf)

    def get_description(self, treeiter):
        """Get the description from a TreeIter"""
        return self.model[treeiter][self.COL_DESCRIPTION]

    def get_command(self, treeiter):
        """Get the command from a TreeIter"""
        return self.model[treeiter][self.COL_COMMAND]

    def get_terminal(self, treeiter):
        """Get the terminal flag from a TreeIter"""
        return self.model[treeiter][self.COL_TERMINAL]

    def get_icon(self, treeiter):
        """Get the icon from a TreeIter"""
        return self.model[treeiter][self.COL_ICON]

    def dump(self):
        """Extract the model data to a dict object"""
        super(self.__class__, self).dump()
        result = {}
        for key in self.rows.iterkeys():
            result[key] = ServiceInfo(
                name=self.get_key(self.rows[key]),
                description=self.get_description(self.rows[key]),
                command=self.get_command(self.rows[key]),
                terminal=self.get_terminal(self.rows[key]),
                icon=self.get_icon(self.rows[key]))
        return result
