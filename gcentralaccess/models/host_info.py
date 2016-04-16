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

from gcentralaccess.models.association_info import AssociationInfo


class HostInfo(object):
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.destinations = {}
        self.associations = []

    def add_destination(self, item):
        """Add a new DestinationInfo object to destinations"""
        self.destinations[item.name] = item

    def clear_destinations(self):
        """Remove any destinations"""
        while self.destinations:
            self.destinations.popitem()

    def add_association(self, description, destination_name, service_name,
                        arguments):
        """Add a new AssociationInfo object to the host"""
        self.associations.append(AssociationInfo(description,
                                                 destination_name,
                                                 service_name,
                                                 arguments))

    def find_association(self, description, destination, service, arguments):
        """Find the AssociationInfo with the corresponding arguments"""
        for association in self.associations:
            if (association.description == description and
                    association.destination_name == destination and
                    association.service_name == service and
                    association.service_arguments == arguments):
                return association
        else:
            return None
