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

import os.path

from gi.repository import Gtk

import gcentralaccess.settings as settings
from gcentralaccess.gtkbuilder_loader import GtkBuilderLoader
from gcentralaccess.functions import (
    check_invalid_input, get_ui_file, set_error_message_on_infobar, text, _)

from gcentralaccess.models.destinations import ModelDestinations
from gcentralaccess.models.destination_info import DestinationInfo

SECTION_WINDOW_NAME = 'destination'


class UIDestination(object):
    def __init__(self, parent, destinations):
        """Prepare the destination dialog"""
        # Load the user interface
        self.ui = GtkBuilderLoader(get_ui_file('destination.glade'))
        self.ui.dialog_destination.set_transient_for(parent)
        # Restore the saved size and position
        settings.positions.restore_window_position(
            self.ui.dialog_destination, SECTION_WINDOW_NAME)
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
        self.model = destinations
        self.selected_iter = None
        self.name = ''
        self.value = ''
        # Connect signals from the glade file to the module functions
        self.ui.connect_signals(self)

    def show(self, default_name, default_value, title, treeiter):
        """Show the destination dialog"""
        self.ui.txt_name.set_text(default_name)
        self.ui.txt_value.set_text(default_value)
        self.ui.txt_name.grab_focus()
        self.ui.dialog_destination.set_title(title)
        self.selected_iter = treeiter
        response = self.ui.dialog_destination.run()
        self.ui.dialog_destination.hide()
        self.name = self.ui.txt_name.get_text().strip()
        self.value = self.ui.txt_value.get_text().strip()
        return response

    def destroy(self):
        """Destroy the destination dialog"""
        settings.positions.save_window_position(
            self.ui.dialog_destination, SECTION_WINDOW_NAME)
        self.ui.dialog_destination.destroy()
        self.ui.dialog_destination = None

    def on_action_confirm_activate(self, action):
        """Check the destination configuration before confirm"""
        def show_error_message_on_infobar(widget, error_msg):
            """Show the error message on the GtkInfoBar"""
            set_error_message_on_infobar(
                widget=widget,
                widgets=(self.ui.txt_name, self.ui.txt_value),
                label=self.ui.lbl_error_message,
                infobar=self.ui.infobar_error_message,
                error_msg=error_msg)
        name = self.ui.txt_name.get_text().strip()
        value = self.ui.txt_value.get_text().strip()
        if len(name) == 0:
            # Show error for missing destination name
            show_error_message_on_infobar(
                self.ui.txt_name,
                _('The destination name is missing'))
        elif '\'' in name or '\\' in name:
            # Show error for invalid destination name
            show_error_message_on_infobar(
                self.ui.txt_name,
                _('The destination name is invalid'))
        elif self.model.get_iter(name) not in (None, self.selected_iter):
            # Show error for existing destination name
            show_error_message_on_infobar(
                self.ui.txt_name,
                _('A destination with that name already exists'))
        elif len(value) == 0:
            # Show error for missing destination value
            show_error_message_on_infobar(
                self.ui.txt_value,
                _('The destination value is missing'))
        else:
            self.ui.dialog_destination.response(Gtk.ResponseType.OK)

    def on_infobar_error_message_response(self, widget, response_id):
        """Close the infobar"""
        if response_id == Gtk.ResponseType.CLOSE:
            self.ui.infobar_error_message.set_visible(False)

    def on_txt_name_changed(self, widget):
        """Check the destination name field"""
        check_invalid_input(widget, False, False, False)
