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

import json

from gcentralaccess.models.abstract import ModelAbstract


class ModelAssociations(ModelAbstract):
    COL_DESTINATION = 1
    COL_SERVICE_NAME = 2
    COL_SERVICE_DESCRIPTION = 3
    COL_SERVICE_ICON = 4
    COL_SERVICE_ARGUMENTS = 5

    def add_data(self, index, name, service, arguments):
        """Add a new row to the model if it doesn't exists"""
        super(self.__class__, self).add_data(service)
        if index not in self.rows:
            new_row = self.model.append((
                index,
                name,
                service.name,
                service.description,
                None,
                json.dumps(arguments)))
            self.rows[index] = new_row
            return new_row

    def set_data(self, treeiter, index, name, service, arguments):
        """Update an existing TreeIter"""
        super(self.__class__, self).set_data(treeiter, service)
        self.model.set_value(treeiter, self.COL_KEY, index)
        self.model.set_value(treeiter, self.COL_DESTINATION, name)
        self.model.set_value(treeiter, self.COL_SERVICE_NAME, service.name)
        self.model.set_value(treeiter, self.COL_SERVICE_DESCRIPTION,
                             service.description)
        self.model.set_value(treeiter, self.COL_SERVICE_ICON, service.icon)
        self.model.set_value(treeiter, self.COL_SERVICE_ARGUMENTS,
                             json.dumps(arguments))

    def get_destination_name(self, treeiter):
        """Get the destination from a TreeIter"""
        return self.model[treeiter][self.COL_DESTINATION]

    def get_service_name(self, treeiter):
        """Get the service name from a TreeIter"""
        return self.model[treeiter][self.COL_SERVICE_NAME]

    def get_arguments(self, treeiter):
        """Get the service arguments from a TreeIter"""
        return json.loads(self.model[treeiter][self.COL_SERVICE_ARGUMENTS])

    def dump(self):
        """Extract the model data to a dict object"""
        super(self.__class__, self).dump()
        result = {}
        for key in self.rows.iterkeys():
            result[key] = (
                self.get_destination_name(self.rows[key]),
                self.get_service_name(self.rows[key]),
                self.get_arguments(self.rows[key]))
        return result
