##
#     Project: gCentralAccess
# Description: Manage external resources from a centralized management console
#      Author: Fabio Castelli (Muflone) <muflone@vbsimple.net>
#   Copyright: 2015 Fabio Castelli
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

from .service_info import ServiceInfo
from .preferences import ICON_SIZE
from gi.repository import GdkPixbuf


class ModelServices(object):
    COL_NAME = 0
    COL_DESCRIPTION = 1
    COL_COMMAND = 2
    COL_TERMINAL = 3
    COL_ICON = 4
    COL_PIXBUF = 5

    def __init__(self, model, preferences):
        self.model = model
        self.rows = {}
        self.icon_size = preferences.get(ICON_SIZE)

    def clear(self):
        """Clear the model"""
        return self.model.clear()

    def add_data(self, item):
        """Add a new row to the model if it doesn't exists"""
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
        old_name = self.get_name(treeiter)
        # If the new name differs from the old name then update the
        # TreeIters map in self.rows
        if old_name != item.name:
            self.rows.pop(old_name)
            self.rows[item.name] = treeiter
        # Update values
        icon = item.icon if item.icon is not None else ''
        pixbuf = None if icon == '' else \
            GdkPixbuf.Pixbuf.new_from_file_at_size(item.icon,
                                                   self.icon_size,
                                                   self.icon_size)
        self.model.set_value(treeiter, self.COL_NAME, item.name)
        self.model.set_value(treeiter, self.COL_DESCRIPTION, item.description)
        self.model.set_value(treeiter, self.COL_COMMAND, item.command)
        self.model.set_value(treeiter, self.COL_TERMINAL, item.terminal)
        self.model.set_value(treeiter, self.COL_ICON, icon)
        self.model.set_value(treeiter, self.COL_PIXBUF, pixbuf)

    def get_name(self, treeiter):
        """Get the name from a TreeIter"""
        return self.model[treeiter][self.COL_NAME]

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

    def get_iter(self, name):
        """Get a TreeIter from a name"""
        return self.rows.get(name)

    def remove(self, treeiter):
        """Remove a TreeIter"""
        self.rows.pop(self.get_name(treeiter))
        self.model.remove(treeiter)

    def dump(self):
        """Extract the model data to a dict object"""
        result = {}
        for key in self.rows.iterkeys():
            result[key] = ServiceInfo(
                name=self.get_name(self.rows[key]),
                description=self.get_description(self.rows[key]),
                command=self.get_command(self.rows[key]),
                terminal=self.get_terminal(self.rows[key]),
                icon=self.get_icon(self.rows[key]))
        return result

    def load(self, items):
        """Load the model data from a dict object"""
        for key in sorted(items.iterkeys()):
            self.add_data(items[key])
