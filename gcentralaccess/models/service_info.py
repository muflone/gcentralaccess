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


class ServiceInfo(object):
    def __init__(self, name, description, command, terminal, icon):
        self.name = name
        self.description = description
        self.command = command
        self.terminal = terminal
        self.icon = icon
        self.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
            icon,
            preferences.get(preferences.ICON_SIZE),
            preferences.get(preferences.ICON_SIZE)) if icon else None
