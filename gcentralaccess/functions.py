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

import os.path
import gi

from gettext import gettext as _
from gettext import dgettext

from .constants import DIR_UI

if gi.require_version('Gtk', '3.0') is None:
    from gi.repository import Gtk
if gi.require_version('GdkPixbuf', '2.0') is None:
    from gi.repository import GdkPixbuf


def readlines(filename, empty_lines=False):
    """Read all the lines of a filename, optionally skipping empty lines"""
    result = []
    with open(filename) as f:
        for line in f.readlines():
            line = line.strip()
            if line or empty_lines:
                result.append(line)
        f.close()
    return result


def process_events():
    """Process every pending GTK+ event"""
    while Gtk.events_pending():
        Gtk.main_iteration()


def gtk30_(message, context=None):
    """Return a message translated from GTK+ 3 domain"""
    return dgettext('gtk30', message if not context else '%s\04%s' % (
        context, message))


def get_ui_file(filename):
    """Return the full path of a Glade/UI file"""
    return os.path.join(DIR_UI, filename)


__all__ = [
    'readlines',
    'process_events',
    '_',
    'gtk30_',
    'get_ui_file'
]
