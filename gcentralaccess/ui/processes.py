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
import subprocess

from gi.repository import Gtk
from gi.repository import GLib

import gcentralaccess.settings as settings
from gcentralaccess.gtkbuilder_loader import GtkBuilderLoader
from gcentralaccess.functions import (
    get_ui_file, get_treeview_selected_row, text, _)

import gcentralaccess.ui.debug as debug

from gcentralaccess.models.process_info import ProcessInfo
from gcentralaccess.models.processes import ModelProcesses

SECTION_WINDOW_NAME = 'processes'

processes = None


class UIProcesses(object):
    def __init__(self, parent, delete_event_cb):
        """Prepare the processes dialog"""
        self.on_window_processes_delete_event = delete_event_cb
        self.processes = {}
        self.poller_id = None
        # Load the user interface
        self.ui = GtkBuilderLoader(get_ui_file('processes.glade'))
        self.ui.window_processes.set_transient_for(parent)
        # Restore the saved size and position
        settings.positions.restore_window_position(
            self.ui.window_processes, SECTION_WINDOW_NAME)
        # Initialize actions
        for widget in self.ui.get_objects_by_type(Gtk.Action):
            # Connect the actions accelerators
            widget.connect_accelerator()
            # Set labels
            widget.set_label(text(widget.get_label()))
        # Initialize tooltips
        for widget in self.ui.get_objects_by_type(Gtk.ToolButton):
            action = widget.get_related_action()
            if action:
                widget.set_tooltip_text(action.get_label().replace('_', ''))
        self.model = ModelProcesses(self.ui.store_processes)
        # Connect signals from the glade file to the module functions
        self.ui.connect_signals(self)

    def show(self):
        """Show the processes dialog"""
        settings.positions.restore_window_position(
            self.ui.window_processes, SECTION_WINDOW_NAME)
        self.ui.window_processes.show()

    def hide(self):
        """Hide the processes dialog"""
        settings.positions.save_window_position(
            self.ui.window_processes, SECTION_WINDOW_NAME)
        self.ui.window_processes.hide()

    def destroy(self):
        """Destroy the Debug dialog"""
        self.hide()
        self.ui.window_processes.destroy()
        self.ui.window_processes = None

    def add_process(self, host, destination, service, command):
        """Add a new process"""
        process = subprocess.Popen(args=command,
                                   shell=True)
        treeiter = self.model.add_data(ProcessInfo(host,
                                                   destination,
                                                   service,
                                                   process))
        # Enable process actions
        self.ui.actions_processes.set_sensitive(True)
        # Save process for further polling
        self.processes[self.model.get_key(treeiter)] = process
        self.model.add_detail(treeiter,
                              _('Process started'),
                              'media-playback-start')
        self.start_polling()

    def poll_processes(self):
        """Poll each process to check if it was terminated"""
        for key in self.processes.keys():
            process = self.processes[key]
            return_code = process.poll()
            # Has the process exited?
            if return_code is not None:
                treeiter = self.model.get_iter(key)
                self.model.add_detail(treeiter,
                                      _('Exit code: %d') % return_code,
                                      'media-playback-stop')
                # Remove the completed process
                self.processes.pop(key)
        if len(self.processes):
            # Continue the polling
            return True
        else:
            # Stop the polling
            self.poller_id = None
            return False

    def start_polling(self):
        """Start the poller timeout if it wasn't already started"""
        if not self.poller_id:
            self.poller_id = GLib.timeout_add(1000, self.poll_processes)

    def on_action_process_activate(self, action):
        """Execute an action for the selected process"""
        selected_row = get_treeview_selected_row(self.ui.tvw_processes)
        if selected_row:
            iter_parent = self.model.model.iter_parent(selected_row)
            selected_path = self.model.model[selected_row].path
            # Get the path of the process
            if iter_parent is None:
                tree_path = self.model.model[selected_row].path
            else:
                tree_path = self.model.model[iter_parent].path
            #
            selected_key = self.model.get_key(tree_path)
            if selected_key in self.processes:
                selected_process = self.processes[selected_key]
                treeiter = self.model.get_iter(selected_key)
                if action is self.ui.action_kill:
                    # Resume the process and terminate it
                    selected_process.send_signal(subprocess.signal.SIGCONT)
                    selected_process.terminate()
                    debug.add_info(
                        _('The process with the PID %d was terminated') % (
                            selected_process.pid))
                    self.model.add_detail(treeiter,
                                          _('Process terminated'),
                                          'media-playback-stop')
                elif action is self.ui.action_pause:
                    # Pause the process by sending the STOP signal
                    selected_process.send_signal(subprocess.signal.SIGSTOP)
                    debug.add_info(
                        _('The process with the PID %d was paused') % (
                            selected_process.pid))
                    self.model.add_detail(treeiter,
                                          _('Process paused'),
                                          'media-playback-pause')
                elif action is self.ui.action_resume:
                    # Pause the process by sending the CONT signal
                    selected_process.send_signal(subprocess.signal.SIGCONT)
                    debug.add_info(
                        _('The process with the PID %d was resumed') % (
                            selected_process.pid))
                    self.model.add_detail(treeiter,
                                          _('Process resumed'),
                                          'media-playback-start')

    def on_tvw_processes_row_activated(self, widget, treepath, column):
        """Expand or collapse the selected row"""
        selected_row = get_treeview_selected_row(self.ui.tvw_processes)
        if selected_row:
            iter_parent = self.ui.store_processes.iter_parent(selected_row)
            selected_path = self.model.model[selected_row].path
            # Get the path of the process
            if iter_parent is None:
                tree_path = self.model.model[selected_row].path
                expanded = self.ui.tvw_processes.row_expanded(tree_path)
                if expanded:
                    self.ui.tvw_processes.collapse_row(tree_path)
                else:
                    self.ui.tvw_processes.expand_row(tree_path, True)
