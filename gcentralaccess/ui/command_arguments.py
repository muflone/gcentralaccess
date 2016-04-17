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

from gi.repository import Gtk

from gcentralaccess.gtkbuilder_loader import GtkBuilderLoader
from gcentralaccess.functions import (
    get_ui_file, get_treeview_selected_row, get_list_from_string_list,
    text, _)
import gcentralaccess.preferences as preferences
import gcentralaccess.settings as settings

from gcentralaccess.ui.command_argument import UICommandArgument
from gcentralaccess.ui.message_dialog import (
    show_message_dialog, UIMessageDialogNoYes)

SECTION_WINDOW_NAME = 'command arguments'


class UICommandArguments(object):
    def __init__(self, parent):
        """Prepare the command arguments dialog"""
        # Load the user interface
        self.ui = GtkBuilderLoader(get_ui_file('command_arguments.glade'))
        if not preferences.get(preferences.DETACHED_WINDOWS):
            self.ui.dialog_arguments.set_transient_for(parent)
        # Restore the saved size and position
        settings.positions.restore_window_position(
            self.ui.dialog_arguments, SECTION_WINDOW_NAME)
        # Initialize actions
        for widget in self.ui.get_objects_by_type(Gtk.Action):
            # Connect the actions accelerators
            widget.connect_accelerator()
            # Set labels
            widget.set_label(text(widget.get_label()))
        # Initialize tooltips
        for widget in self.ui.get_objects_by_type(Gtk.Button):
            action = widget.get_related_action()
            if action:
                widget.set_tooltip_text(action.get_label().replace('_', ''))
        # Initialize column headers
        for widget in self.ui.get_objects_by_type(Gtk.TreeViewColumn):
            widget.set_title(text(widget.get_title()))
        # Load the arguments
        self.model_arguments = self.ui.store_arguments
        self.arguments = '[]'
        # Connect signals from the glade file to the module functions
        self.ui.connect_signals(self)

    def show(self, default_command):
        """Show the command arguments dialog"""
        arguments = get_list_from_string_list(default_command)
        for argument in arguments:
            self.model_arguments.append((argument, ))
        self.ui.dialog_arguments.run()
        self.ui.dialog_arguments.hide()
        arguments = []
        for treeiter in self.model_arguments:
            arguments.append(self.model_arguments[treeiter.path][0])
        self.arguments = json.dumps(arguments)

    def destroy(self):
        """Destroy the command arguments dialog"""
        settings.positions.save_window_position(
            self.ui.dialog_arguments, SECTION_WINDOW_NAME)
        self.ui.dialog_arguments.destroy()
        self.ui.dialog_arguments = None

    def on_action_add_activate(self, action):
        """Add a new argument"""
        dialog = UICommandArgument(self.ui.dialog_arguments)
        if dialog.show(default_value='') == Gtk.ResponseType.OK:
            self.model_arguments.append((dialog.argument, ))
        dialog.destroy()

    def on_action_edit_activate(self, action):
        """Edit the selected service"""
        selected_row = get_treeview_selected_row(self.ui.tvw_arguments)
        if selected_row:
            argument = self.model_arguments[selected_row][0]
            dialog = UICommandArgument(self.ui.dialog_arguments)
            if dialog.show(default_value=argument) == Gtk.ResponseType.OK:
                # Update values
                self.model_arguments.set_value(selected_row, 0,
                                               dialog.argument)
            dialog.destroy()

    def on_action_remove_activate(self, action):
        """Remove the selected service"""
        selected_row = get_treeview_selected_row(self.ui.tvw_arguments)
        if selected_row and show_message_dialog(
                class_=UIMessageDialogNoYes,
                parent=self.ui.dialog_arguments,
                message_type=Gtk.MessageType.WARNING,
                title=None,
                msg1=_("Remove argument"),
                msg2=_("Remove the selected argument?"),
                is_response_id=Gtk.ResponseType.YES):
            self.model_arguments.remove(selected_row)

    def on_tvw_arguments_row_activated(self, widget, treepath, column):
        """Edit the selected row on activation"""
        self.ui.action_edit.activate()
