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

import gcentralaccess.settings as settings

SAVE_DEFAULT_VALUES = False
DEFAULT_VALUES = {}

SECTION_PREFERENCES = 'preferences'
SECTION_DEBUG = 'debug'

ICON_SIZE = 'icon size'
DEFAULT_VALUES[ICON_SIZE] = (SECTION_PREFERENCES, 36)

PREVIEW_SIZE = 'preview size'
DEFAULT_VALUES[PREVIEW_SIZE] = (SECTION_PREFERENCES, 128)

DEBUG_ENABLED = 'debug enabled'
DEFAULT_VALUES[DEBUG_ENABLED] = (SECTION_DEBUG, False)

DEBUG_ENABLED_HIDDEN = 'debug enabled if hidden'
DEFAULT_VALUES[DEBUG_ENABLED_HIDDEN] = (SECTION_DEBUG, False)

DEBUG_SHOW_INFO = 'debug show info'
DEFAULT_VALUES[DEBUG_SHOW_INFO] = (SECTION_DEBUG, True)

DEBUG_SHOW_WARNING = 'debug show warning'
DEFAULT_VALUES[DEBUG_SHOW_WARNING] = (SECTION_DEBUG, True)

DEBUG_SHOW_ERROR = 'debug show error'
DEFAULT_VALUES[DEBUG_SHOW_ERROR] = (SECTION_DEBUG, True)

DEBUG_TIMESTAMP = 'debug timestamp'
DEFAULT_VALUES[DEBUG_TIMESTAMP] = (SECTION_DEBUG, False)

DEBUG_FOLLOW_TEXT = 'debug follow text'
DEFAULT_VALUES[DEBUG_FOLLOW_TEXT] = (SECTION_DEBUG, False)

preferences = None


class Preferences(object):
    def __init__(self):
        """Load settings into preferences"""
        self.options = {}
        for option in DEFAULT_VALUES.keys():
            section, default = DEFAULT_VALUES[option]
            if isinstance(default, int):
                self.options[option] = settings.settings.get_int(
                    section, option, default)
            elif isinstance(default, bool):
                self.options[option] = settings.settings.get_boolean(
                    section, option, default)
            else:
                self.options[option] = settings.settings.get(
                    section, option, default)
            # Save the default value
            if SAVE_DEFAULT_VALUES:
                self.set(option, default)

    def get(self, option):
        """Returns a preferences option"""
        return self.options[option]

    def set(self, option, value):
        """Set a preferences option"""
        self.options[option] = value
        if option in DEFAULT_VALUES:
            section, default = DEFAULT_VALUES[option]
            if value != default or SAVE_DEFAULT_VALUES:
                if isinstance(default, bool):
                    settings.settings.set_boolean(section, option, value)
                elif isinstance(default, int):
                    settings.settings.set_int(section, option, value)
                else:
                    settings.settings.set(section, option, value)
            else:
                # Remove old option value
                settings.settings.unset_option(section, option)


def get(option):
    """Returns a preferences option"""
    if preferences:
        return preferences.get(option)


def set(option, value):
    """Set a preferences option"""
    if preferences:
        return preferences.set(option, value)
