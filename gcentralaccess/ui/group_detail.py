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

from gi.repository import Gtk

import gcentralaccess.preferences as preferences
from gcentralaccess.gtkbuilder_loader import GtkBuilderLoader
from gcentralaccess.functions import (
    check_invalid_input, get_ui_file, set_error_message_on_infobar, text, _)


class UIGroupDetail(object):
    def __init__(self, parent, groups):
        """Prepare the group detail dialog"""
        # Load the user interface
        self.ui = GtkBuilderLoader(get_ui_file('group_detail.glade'))
        if not preferences.get(preferences.DETACHED_WINDOWS):
            self.ui.dialog_edit_group.set_transient_for(parent)
        # Initialize actions
        for widget in self.ui.get_objects_by_type(Gtk.Action):
            # Connect the actions accelerators
            widget.connect_accelerator()
            # Set labels
            widget.set_label(text(widget.get_label()))
        # Initialize labels
        for widget in self.ui.get_objects_by_type(Gtk.Label):
            widget.set_label(text(widget.get_label()))
            widget.set_tooltip_text(widget.get_label().replace('_', ''))
        # Initialize tooltips
        for widget in self.ui.get_objects_by_type(Gtk.Button):
            action = widget.get_related_action()
            if action:
                widget.set_tooltip_text(action.get_label().replace('_', ''))
        self.model = groups
        self.name = ''
        # Connect signals from the glade file to the module functions
        self.ui.connect_signals(self)

    def show(self, default_name, title, treeiter):
        """Show the Group detail dialog"""
        self.ui.txt_name.set_text(default_name)
        self.ui.txt_name.grab_focus()
        self.ui.dialog_edit_group.set_title(title)
        response = self.ui.dialog_edit_group.run()
        self.ui.dialog_edit_group.hide()
        self.name = self.ui.txt_name.get_text().strip()
        return response

    def destroy(self):
        """Destroy the Group detail dialog"""
        self.ui.dialog_edit_group.destroy()
        self.ui.dialog_edit_group = None

    def on_action_confirm_activate(self, action):
        """Check che group configuration before confirm"""
        def show_error_message_on_infobar(widget, error_msg):
            """Show the error message on the GtkInfoBar"""
            set_error_message_on_infobar(
                widget=widget,
                widgets=(self.ui.txt_name, ),
                label=self.ui.lbl_error_message,
                infobar=self.ui.infobar_error_message,
                error_msg=error_msg)
        name = self.ui.txt_name.get_text().strip()
        if len(name) == 0:
            # Show error for missing group name
            show_error_message_on_infobar(
                self.ui.txt_name,
                _('The group name is missing'))
        elif '\'' in name or '\\' in name or '/' in name or ',' in name:
            # Show error for invalid group name
            show_error_message_on_infobar(
                self.ui.txt_name,
                _('The Group name is invalid'))
        elif self.model.get_iter(name):
            # Show error for existing group name
            show_error_message_on_infobar(
                self.ui.txt_name,
                _('A group with that name already exists'))
        else:
            self.ui.dialog_edit_group.response(Gtk.ResponseType.OK)

    def on_infobar_error_message_response(self, widget, response_id):
        """Close the infobar"""
        if response_id == Gtk.ResponseType.CLOSE:
            self.ui.infobar_error_message.set_visible(False)

    def on_txt_name_changed(self, widget):
        """Check the group name field"""
        check_invalid_input(widget, False, False, False)
