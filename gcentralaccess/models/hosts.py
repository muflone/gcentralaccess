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

from gcentralaccess.models.abstract import ModelAbstract
from gcentralaccess.models.host_info import HostInfo


class ModelHosts(ModelAbstract):
    COL_DESCRIPTION = 1
    COL_SERVICE = 2
    COL_ICON = 3

    def __init__(self, model, preferences):
        super(self.__class__, self).__init__(model, preferences)
        self.destinations = {}

    def add_data(self, item):
        """Add a new row to the model if it doesn't exists"""
        super(self.__class__, self).add_data(item)
        if item.name not in self.rows:
            new_row = self.model.append(None, (item.name,
                                               item.description,
                                               '',
                                               None))
            self.rows[item.name] = new_row
            self.destinations[item.name] = {}
            return new_row

    def remove(self, treeiter):
        """Remove a TreeIter"""
        self.destinations.pop(self.get_key(treeiter))
        super(self.__class__, self).remove(treeiter)

    def add_destination(self, name, destination):
        """Add a new destination if it doesn't exists"""
        if destination.name not in self.destinations[name]:
            self.destinations[name][destination.name] = destination

    def get_destinations(self, name):
        """Get the destinations for the requested host"""
        return self.destinations.get(name, None)

    def clear_destinations(self, name):
        """Clear the destinations for the requested host"""
        if name in self.destinations:
            while self.destinations[name]:
                self.destinations[name].popitem()

    def set_data(self, treeiter, item):
        """Update an existing TreeIter"""
        super(self.__class__, self).set_data(treeiter, item)
        # Update values
        self.model.set_value(treeiter, self.COL_KEY, item.name)
        self.model.set_value(treeiter, self.COL_DESCRIPTION, item.description)

    def get_value(self, treeiter):
        """Get the value from a TreeIter"""
        return self.model[treeiter][self.COL_VALUE]

    def get_description(self, treeiter):
        """Get the description from a TreeIter"""
        return self.model[treeiter][self.COL_DESCRIPTION]
