# -*- coding: UTF-8 -*-
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

import os
import os.path

from gi.repository import Gtk

from gcentralaccess.gtkbuilder_loader import GtkBuilderLoader
from gcentralaccess.constants import DIR_HOSTS
from gcentralaccess.functions import (
    get_ui_file, get_treeview_selected_row, text, _)
import gcentralaccess.preferences as preferences
import gcentralaccess.settings as settings

from gcentralaccess.models.groups import ModelGroups
from gcentralaccess.models.group_info import GroupInfo

import gcentralaccess.ui.debug as debug
from gcentralaccess.ui.group_detail import UIGroupDetail
from gcentralaccess.ui.message_dialog import (
    show_message_dialog, UIMessageDialogNoYes)

SECTION_WINDOW_NAME = 'groups'


class UIGroups(object):
    def __init__(self, parent):
        """Prepare the groups dialog"""
        # Load the user interface
        self.ui = GtkBuilderLoader(get_ui_file('groups.glade'))
        if not preferences.get(preferences.DETACHED_WINDOWS):
            self.ui.dialog_groups.set_transient_for(parent)
        # Restore the saved size and position
        settings.positions.restore_window_position(
            self.ui.dialog_groups, SECTION_WINDOW_NAME)
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
        # Load the groups
        self.model = ModelGroups(self.ui.store_groups)
        self.selected_iter = None
        # Sort the data in the models
        self.model.model.set_sort_column_id(
            self.ui.column_name.get_sort_column_id(),
            Gtk.SortType.ASCENDING)
        # Connect signals from the glade file to the module functions
        self.ui.connect_signals(self)

    def show(self):
        """Show the Groups dialog"""
        self.ui.dialog_groups.run()
        self.ui.dialog_groups.hide()

    def destroy(self):
        """Destroy the Groups dialog"""
        settings.positions.save_window_position(
            self.ui.dialog_groups, SECTION_WINDOW_NAME)
        self.ui.dialog_groups.destroy()
        self.ui.dialog_groups = None

    def on_action_add_activate(self, action):
        """Add a new group"""
        dialog = UIGroupDetail(self.ui.dialog_groups, self.model)
        if dialog.show(default_name='',
                       title=_('Add new group'),
                       treeiter=None) == Gtk.ResponseType.OK:
            os.mkdir(os.path.join(DIR_HOSTS, dialog.name))
            self.model.add_data(GroupInfo(name=dialog.name,
                                          description=dialog.name))
            debug.add_info(_('Added a new group "%s"') % dialog.name)
        dialog.destroy()

    def on_action_remove_activate(self, action):
        """Remove the selected group"""
        selected_row = get_treeview_selected_row(self.ui.tvw_groups)
        group_name = self.model.get_key(selected_row) if selected_row else ''
        if selected_row and group_name and show_message_dialog(
                class_=UIMessageDialogNoYes,
                parent=self.ui.dialog_groups,
                message_type=Gtk.MessageType.WARNING,
                title=None,
                msg1=_('Remove the group'),
                msg2=_('Remove the group «%s»?') % group_name,
                is_response_id=Gtk.ResponseType.YES):
            group_path = os.path.join(DIR_HOSTS, group_name)
            # Check for directory not empty
            if len(os.listdir(group_path)) and not show_message_dialog(
                    class_=UIMessageDialogNoYes,
                    parent=self.ui.dialog_groups,
                    message_type=Gtk.MessageType.WARNING,
                    title=None,
                    msg1=_('The group is not empty'),
                    msg2='%s\n%s\n\n%s' % (
                        text('If you delete an item, it will '
                             'be permanently lost.'),
                        _('All the hosts defined for the group will be lost.'),
                        _('Are you sure you want to delete the '
                          'group «%s»?') % group_name,
                                       ),
                    is_response_id=Gtk.ResponseType.YES):
                # Exit immediately without deleting the group
                return
            # Delete all the contained files and the directory for the group
            for filename in os.listdir(group_path):
                os.remove(os.path.join(group_path, filename))
            os.rmdir(group_path)
            debug.add_info(_('Removed the group "%s"') % group_name)
            self.model.remove(selected_row)
