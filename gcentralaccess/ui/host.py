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

from gcentralaccess.gtkbuilder_loader import GtkBuilderLoader
from gcentralaccess.functions import (
    check_invalid_input, get_ui_file, set_error_message_on_infobar, _)
from gcentralaccess.preferences import ICON_SIZE

from gcentralaccess.models.destinations import ModelDestinations
from gcentralaccess.models.destination_info import DestinationInfo

from gcentralaccess.ui.destination import UIDestination
from gcentralaccess.ui.message_dialog import (
    show_message_dialog, UIMessageDialogNoYes)

SECTION_WINDOW_NAME = 'host'


class UIHost(object):
    def __init__(self, parent, hosts, preferences, settings_positions):
        """Prepare the host dialog"""
        self.preferences = preferences
        self.settings_positions = settings_positions
        self.hosts = hosts
        # Load the user interface
        self.ui = GtkBuilderLoader(get_ui_file('host.glade'))
        self.ui.dialog_host.set_transient_for(parent)
        # Restore the saved size and position
        self.settings_positions.restore_window_position(
            self.ui.dialog_host, SECTION_WINDOW_NAME)
        # Initialize actions
        for widget in self.ui.get_objects_by_type(Gtk.Action):
            # Connect the actions accelerators
            widget.connect_accelerator()
        # Load the destinations
        self.destinations = ModelDestinations(
            self.ui.store_destinations, preferences)
        self.selected_iter = None
        # Connect signals from the glade file to the module functions
        self.ui.connect_signals(self)

    def show(self, default_name, default_description, title, treeiter):
        """Show the destinations dialog"""
        self.ui.txt_name.set_text(default_name)
        self.ui.txt_description.set_text(default_description)
        self.ui.txt_name.grab_focus()
        self.ui.dialog_host.set_title(title)
        self.selected_iter = treeiter
        response = self.ui.dialog_host.run()
        self.ui.dialog_host.hide()
        self.name = self.ui.txt_name.get_text().strip()
        self.description = self.ui.txt_description.get_text().strip()
        return response

    def destroy(self):
        """Destroy the destinations dialog"""
        self.settings_positions.save_window_position(
            self.ui.dialog_host, SECTION_WINDOW_NAME)
        self.ui.dialog_host.destroy()
        self.ui.dialog_host = None

    def on_action_add_activate(self, action):
        """Add a new destination"""
        dialog = UIDestination(self.ui.dialog_host,
                               self.destinations,
                               self.preferences,
                               self.settings_positions)
        if dialog.show(default_name='',
                       default_value='',
                       default_type='ipv4',
                       title=_('Add new destination'),
                       treeiter=None) == Gtk.ResponseType.OK:
            self.destinations.add_data(DestinationInfo(name=dialog.name,
                                                       value=dialog.value,
                                                       type=dialog.type))
        # Get the new destinations list, clear and store the list again
        dialog.destroy()

    def on_action_edit_activate(self, action):
        """Edit the selected destination"""
        selection = self.ui.tvw_destinations.get_selection().get_selected()
        selected_row = selection[1]
        if selected_row:
            name = self.destinations.get_key(selected_row)
            value = self.destinations.get_value(selected_row)
            destination_type = self.destinations.get_type(selected_row)
            selected_iter = self.destinations.get_iter(name)
            dialog = UIDestination(self.ui.dialog_host,
                                   self.destinations,
                                   self.preferences,
                                   self.settings_positions)
            if dialog.show(default_name=name,
                           default_value=value,
                           default_type=destination_type,
                           title=_('Edit destination'),
                           treeiter=selected_iter
                           ) == Gtk.ResponseType.OK:
                # Update values
                self.destinations.set_data(
                    selected_iter, DestinationInfo(name=dialog.name,
                                                   value=dialog.value,
                                                   type=dialog.type))
            dialog.destroy()

    def on_action_remove_activate(self, action):
        """Remove the selected destination"""
        selection = self.ui.tvw_destinations.get_selection().get_selected()
        selected_row = selection[1]
        if selected_row and show_message_dialog(
                class_=UIMessageDialogNoYes,
                parent=self.ui.dialog_host,
                message_type=Gtk.MessageType.QUESTION,
                title=None,
                msg1=_("Remove destination"),
                msg2=_("Remove the selected destination?"),
                is_response_id=Gtk.ResponseType.YES):
            self.destinations.remove(selected_row)

    def on_tvw_destinations_row_activated(self, widget, treepath, column):
        """Edit the selected row on activation"""
        self.ui.action_edit.activate()

    def on_action_confirm_activate(self, action):
        """Check che host configuration before confirm"""
        def show_error_message_on_infobar(widget, error_msg):
            """Show the error message on the GtkInfoBar"""
            set_error_message_on_infobar(
                widget=widget,
                widgets=(self.ui.txt_name, self.ui.txt_description),
                label=self.ui.lbl_error_message,
                infobar=self.ui.infobar_error_message,
                error_msg=error_msg)
        name = self.ui.txt_name.get_text().strip()
        description = self.ui.txt_description.get_text().strip()
        if len(name) == 0:
            # Show error for missing host name
            show_error_message_on_infobar(
                self.ui.txt_name,
                _('The host name is missing'))
        elif '\'' in name or '\\' in name or '/' in name:
            # Show error for invalid host name
            show_error_message_on_infobar(
                self.ui.txt_name,
                _('The host name is invalid'))
        elif self.hosts.get_iter(name) not in (None, self.selected_iter):
            # Show error for existing host name
            show_error_message_on_infobar(
                self.ui.txt_name,
                _('A host with that name already exists'))
        elif len(description) == 0:
            # Show error for missing host description
            show_error_message_on_infobar(
                self.ui.txt_description,
                _('The host description is missing'))
        else:
            self.ui.dialog_host.response(Gtk.ResponseType.OK)

    def on_infobar_error_message_response(self, widget, response_id):
        """Close the infobar"""
        if response_id == Gtk.ResponseType.CLOSE:
            self.ui.infobar_error_message.set_visible(False)

    def on_txt_name_changed(self, widget):
        """Check the host name field"""
        check_invalid_input(widget, False, False, False)

    def on_txt_description_changed(self, widget):
        """Check the host description field"""
        check_invalid_input(widget, False, True, True)
