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
from gi.repository import GdkPixbuf

from gcentralaccess.gtkbuilder_loader import GtkBuilderLoader
from gcentralaccess.functions import get_ui_file, text

import gcentralaccess.models.services as model_services
from gcentralaccess.models.services import ModelServices

SECTION_WINDOW_NAME = 'association'


class UIServiceAssociation(object):
    def __init__(self, parent, destinations):
        """Prepare the service association dialog"""
        # Load the user interface
        self.ui = GtkBuilderLoader(get_ui_file('service_association.glade'))
        self.ui.dialog_association.set_transient_for(parent)
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
        # Load destinations
        self.destinations = destinations
        self.ui.cbo_destinations.set_model(self.destinations.model)
        # Load services
        self.services = ModelServices(self.ui.store_services)
        self.services.load(model_services.services)
        # Connect signals from the glade file to the module functions
        self.ui.connect_signals(self)

    def show(self, default_destination, default_service):
        """Show the Service association dialog"""
        # Set default destination
        if default_destination:
            self.ui.cbo_destinations.set_active_id(default_destination)
            self.ui.cbo_destinations.set_sensitive(False)
        elif self.destinations.count() > 0:
            self.ui.cbo_destinations.set_active(0)
        # Set default service
        if default_service:
            self.ui.cbo_services.set_active_id(default_service)
        elif self.services.count() > 0:
            self.ui.cbo_services.set_active(0)
        # Show the dialog
        response = self.ui.dialog_association.run()
        self.ui.dialog_association.hide()
        self.destination = self.ui.cbo_destinations.get_active_id()
        self.service = self.ui.cbo_services.get_active_id()
        return response

    def destroy(self):
        """Destroy the Service association dialog"""
        self.ui.dialog_association.destroy()
        self.ui.dialog_association = None
