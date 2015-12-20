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

SECTION_PREFERENCES = 'preferences'

ICON_SIZE = 'icon size'
DEFAULT_ICON_SIZE = 36

PREVIEW_SIZE = 'preview size'
DEFAULT_PREVIEW_SIZE = 128


class Preferences(object):
    def __init__(self, settings):
        """Load settings into preferences"""
        self.settings = settings
        self.options = {}
        self.options[ICON_SIZE] = self.settings.get_int(
            SECTION_PREFERENCES, ICON_SIZE, DEFAULT_ICON_SIZE)
        self.options[PREVIEW_SIZE] = self.settings.get_int(
            SECTION_PREFERENCES, PREVIEW_SIZE, DEFAULT_PREVIEW_SIZE)

    def get(self, option):
        """Returns a preferences option"""
        return self.options[option]

    def set(self, option, value):
        """Set a preferences option"""
        self.options[option] = value
        if isinstance(value, int):
            self.settings.set_int(SECTION_PREFERENCES, option, value)
        elif isinstance(value, bool):
            self.settings.set_boolean(SECTION_PREFERENCES, option, value)
        else:
            self.settings.set(SECTION_PREFERENCES, option, value)
