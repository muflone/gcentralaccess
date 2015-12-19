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

from gi.repository import Gtk


class UIFileChooser(Gtk.Window):
    def __init__(self, win_parent, title, action, buttons):
        """Prepare the file chooser dialog"""
        self.dialog = Gtk.FileChooserDialog(title, win_parent, action, buttons)

    def show(self):
        """Show the dialog"""
        result = self.dialog.run()
        self.dialog.hide()
        if result == Gtk.ResponseType.OK:
            return self.dialog.get_filename()

    def destroy(self):
        """Destroy the dialog"""
        self.dialog.destroy()
        self.dialog = None

    def add_filter(self, title, mime_types=None, file_patterns=None):
        """Add a new filter to the dialog"""
        new_filter = Gtk.FileFilter()
        new_filter.set_name(title)
        if mime_types:
            new_filter.add_mime_type(mime_types)
        if file_patterns:
            new_filter.add_pattern(file_patterns)
        self.dialog.add_filter(new_filter)

    def get_local_only(self):
        """Get the local only flag"""
        return self.dialog.get_local_only()

    def set_local_only(self, flag):
        """Set the local only flag"""
        return self.dialog.set_local_only(flag)

    def get_filename(self):
        """Get the selected file name"""
        return self.dialog.get_filename()

    def set_filename(self, file_name):
        """Set the selected file name"""
        return self.dialog.set_filename(file_name)

    def get_uri(self):
        """Get the selected URI"""
        return self.dialog.get_uri()

    def set_uri(self, uri):
        """Set the selected URI"""
        return self.dialog.set_uri(uri)

    def get_current_folder(self):
        """Get the current folder"""
        return self.dialog.get_current_folder()

    def set_current_folder(self, folder_name):
        """Set the current folder"""
        return self.dialog.set_current_folder(folder_name)
