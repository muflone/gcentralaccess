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

from .abstract import ModelAbstract
from .destination_info import DestinationInfo


class ModelDestinations(ModelAbstract):
    COL_VALUE = 1
    COL_TYPE = 2

    def add_data(self, item):
        """Add a new row to the model if it doesn't exists"""
        super(self.__class__, self).add_data(item)
        if item.name not in self.rows:
            new_row = self.model.append((
                item.name,
                item.value,
                item.type))
            self.rows[item.name] = new_row
            return new_row

    def set_data(self, treeiter, item):
        """Update an existing TreeIter"""
        super(self.__class__, self).set_data(treeiter, item)
        # Update values
        self.model.set_value(treeiter, self.COL_KEY, item.name)
        self.model.set_value(treeiter, self.COL_VALUE, item.value)
        self.model.set_value(treeiter, self.COL_TYPE, item.type)

    def get_value(self, treeiter):
        """Get the value from a TreeIter"""
        return self.model[treeiter][self.COL_VALUE]

    def get_type(self, treeiter):
        """Get the type from a TreeIter"""
        return self.model[treeiter][self.COL_TYPE]

    def dump(self):
        """Extract the model data to a dict object"""
        super(self.__class__, self).dump()
        result = {}
        for key in self.rows.iterkeys():
            result[key] = DestinationInfo(
                name=self.get_key(self.rows[key]),
                value=self.get_value(self.rows[key]),
                type=self.get_type(self.rows[key]))
        return result
