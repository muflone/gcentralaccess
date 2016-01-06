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

from gcentralaccess.models.abstract import ModelAbstract
from gcentralaccess.models.destination_type_info import DestinationTypeInfo

destination_types = None


class ModelDestinationTypes(ModelAbstract):
    COL_DESCRIPTION = 1
    COL_PLACEHOLDER = 2

    def add_data(self, item):
        """Add a new row to the model if it doesn't exists"""
        super(self.__class__, self).add_data(item)
        if item.name not in self.rows:
            new_row = self.model.append((
                item.name,
                item.description,
                item.placeholder))
            self.rows[item.name] = new_row
            return new_row

    def set_data(self, treeiter, item):
        """Update an existing TreeIter"""
        super(self.__class__, self).set_data(treeiter, item)
        # Update values
        self.model.set_value(treeiter, self.COL_KEY, item.name)
        self.model.set_value(treeiter, self.COL_DESCRIPTION, item.description)
        self.model.set_value(treeiter, self.COL_PLACEHOLDER, item.placeholder)

    def get_description(self, treeiter):
        """Get the description from a TreeIter"""
        return self.model[treeiter][self.COL_DESCRIPTION]

    def get_placeholder(self, treeiter):
        """Get the placeholder from a TreeIter"""
        return self.model[treeiter][self.COL_PLACEHOLDER]


def get_iter(destination_type):
    return destination_types.get_iter(destination_type)

def get_description(treeiter):
    return destination_types.get_description(treeiter)

def get_placeholder(treeiter):
    return destination_types.get_placeholder(treeiter)

def get_model():
    return destination_types.model
