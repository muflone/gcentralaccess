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

from gi.repository import Gtk
from gi.repository import GdkPixbuf

from gcentralaccess.gtkbuilder_loader import GtkBuilderLoader
from gcentralaccess.functions import get_ui_file, _
from gcentralaccess.preferences import ICON_SIZE, PREVIEW_SIZE
from .file_chooser import UIFileChooserOpenFile

SECTION_WINDOW_NAME = 'services'


class UIServiceDetail(object):
    def __init__(self, parent, services, preferences):
        """Prepare the services detail dialog"""
        # Load the user interface
        self.ui = GtkBuilderLoader(get_ui_file('services_detail.glade'))
        self.ui.dialog_edit_service.set_transient_for(parent)
        # Connect the actions accelerators
        for group_name in ('actions_edit_service', ):
            for action in self.ui.get_object(group_name).list_actions():
                action.connect_accelerator()
        self.model = services
        self.selected_iter = None
        self.name = ''
        self.description = ''
        self.command = ''
        self.terminal = False
        self.icon = ''
        # Load settings
        self.icon_size = preferences.get(ICON_SIZE)
        self.preview_size = preferences.get(PREVIEW_SIZE)
        # Connect signals from the glade file to the module functions
        self.ui.connect_signals(self)

    def show(self, default_name, default_description, default_command,
             default_terminal, default_icon, title, treeiter):
        """Show the Services detail dialog"""
        self.ui.txt_name.set_text(default_name)
        self.ui.txt_description.set_text(default_description)
        self.ui.txt_command.set_text(default_command)
        self.ui.chk_terminal.set_active(default_terminal)
        self.ui.txt_icon.set_text(default_icon)
        self.ui.txt_name.grab_focus()
        self._edit_service_set_error(None, None)
        self.ui.dialog_edit_service.set_title(title)
        self.selected_iter = treeiter
        response = self.ui.dialog_edit_service.run()
        self.ui.dialog_edit_service.hide()
        self.name = self.ui.txt_name.get_text().strip()
        self.description = self.ui.txt_description.get_text().strip()
        self.command = self.ui.txt_command.get_text().strip()
        self.terminal = self.ui.chk_terminal.get_active()
        self.icon = self.ui.txt_icon.get_text().strip()
        return response

    def destroy(self):
        """Destroy the Services dialog"""
        self.ui.dialog_edit_service.destroy()
        self.ui.dialog_edit_service = None

    def on_action_confirm_activate(self, action):
        """Check che service configuration before confirm"""
        name = self.ui.txt_name.get_text().strip()
        description = self.ui.txt_description.get_text().strip()
        command = self.ui.txt_command.get_text().strip()
        terminal = self.ui.chk_terminal.get_active()
        icon = self.ui.txt_icon.get_text().strip()
        if len(name) == 0:
            self._edit_service_set_error(
                self.ui.txt_name,
                _('The service name is missing'))
        elif '\'' in name or '\\' in name:
            self._edit_service_set_error(
                self.ui.txt_name,
                _('The service name is invalid'))
        elif self.model.get_iter(name) not in (None, self.selected_iter):
            self._edit_service_set_error(
                self.ui.txt_name,
                _('A service with that name already exists'))
        elif len(description) == 0:
            self._edit_service_set_error(
                self.ui.txt_description,
                _('The service description is missing'))
        elif '\'' in description or '\\' in description:
            self._edit_service_set_error(
                self.ui.txt_description,
                _('The service description is invalid'))
        elif len(command) == 0:
            self._edit_service_set_error(
                self.ui.txt_command,
                _('The service command is missing'))
        elif len(icon) > 0 and not os.path.isfile(icon):
            self._edit_service_set_error(
                self.ui.txt_icon,
                _('The service icon doesn\'t exists'))
        else:
            self.ui.dialog_edit_service.response(Gtk.ResponseType.OK)

    def on_infobar_error_message_response(self, widget, response_id):
        """Close the infobar"""
        if response_id == Gtk.ResponseType.CLOSE:
            self.ui.infobar_error_message.set_visible(False)

    def _edit_service_set_error(self, widget, error_message):
        """Show an error message for a widget"""
        if error_message:
            self.ui.lbl_error_message.set_text(error_message)
            self.ui.infobar_error_message.set_visible(True)
            if widget in (self.ui.txt_name,
                          self.ui.txt_description,
                          self.ui.txt_command):
                widget.set_icon_from_icon_name(
                    Gtk.EntryIconPosition.SECONDARY, 'dialog-error')
                widget.grab_focus()
        else:
            self.ui.infobar_error_message.set_visible(False)
            self.ui.txt_name.set_icon_from_icon_name(
                Gtk.EntryIconPosition.SECONDARY, None)
            self.ui.txt_description.set_icon_from_icon_name(
                Gtk.EntryIconPosition.SECONDARY, None)
            self.ui.txt_command.set_icon_from_icon_name(
                Gtk.EntryIconPosition.SECONDARY, None)

    def on_txt_name_description_changed(self, widget):
        """Check the service name or description fields"""
        text = widget.get_text().strip()
        if len(text) == 0 or '\'' in text or '\\' in text:
            icon_name = 'dialog-error'
        else:
            icon_name = None
        widget.set_icon_from_icon_name(
            Gtk.EntryIconPosition.SECONDARY, icon_name)

    def on_txt_icon_changed(self, widget):
        """Check the icon field"""
        text = widget.get_text().strip()
        if len(text) > 0 and os.path.isfile(text):
            self.ui.image_icon.set_from_pixbuf(
                GdkPixbuf.Pixbuf.new_from_file_at_size(text,
                                                       self.icon_size,
                                                       self.icon_size))
            icon_name = None
        else:
            icon_name = 'dialog-error' if len(text) > 0 else None
            self.ui.image_icon.set_from_icon_name('image-missing',
                                                  Gtk.IconSize.LARGE_TOOLBAR)
        widget.set_icon_from_icon_name(
            Gtk.EntryIconPosition.SECONDARY, icon_name)

    def on_action_browse_icon_activate(self, action):
        """Browse for an icon file"""
        def update_preview_cb(widget, image, get_preview_filename, set_active):
            """Update preview by trying to load the image"""
            try:
                # Try to load the image from the previewed file
                image.set_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file_at_size(
                    get_preview_filename(),
                    self.preview_size,
                    self.preview_size))
                set_active(True)
            except:
                # Hide the preview widget for errors
                image.set_from_pixbuf(None)
                set_active(False)
        # Prepare the browse for icon dialog
        dialog = UIFileChooserOpenFile(self.ui.dialog_edit_service,
                                       _("Select an icon"))
        dialog.add_filter(_("All Image Files"), "image/*", None)
        dialog.add_filter(_("All Files"), None, "*")
        dialog.set_filename(self.ui.txt_icon.get_text())
        # Set the image preview widget
        image_preview = Gtk.Image()
        image_preview.set_hexpand(False)
        image_preview.set_size_request(self.preview_size, -1)
        dialog.set_preview_widget(image_preview, update_preview_cb)
        # Show the browse for icon dialog
        filename = dialog.show()
        if filename is not None:
            self.ui.txt_icon.set_text(filename)
        dialog.destroy()
