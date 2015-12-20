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

import sys
import os.path
from xdg import BaseDirectory

# Application constants
APP_NAME = 'gCentralAccess'
APP_VERSION = '0.0.1'
APP_DESCRIPTION = 'Manage external resources from a centralized management ' \
    'console'
APP_ID = 'gcentralaccess.muflone.com'
APP_URL = 'http://www.muflone.com/gcentralaccess/'
APP_AUTHOR = 'Fabio Castelli'
APP_AUTHOR_EMAIL = 'muflone@vbsimple.net'
APP_COPYRIGHT = 'Copyright 2015 %s' % APP_AUTHOR
# Other constants
DOMAIN_NAME = 'gcentralaccess'
VERBOSE_LEVEL_QUIET = 0
VERBOSE_LEVEL_NORMAL = 1
VERBOSE_LEVEL_MAX = 2

# Paths constants
# If there's a file data/gcentralaccess.png then the shared data are searched
# in relative paths, else the standard paths are used
if os.path.isfile(os.path.join('data', 'gcentralaccess.png')):
    DIR_PREFIX = '.'
    DIR_LOCALE = os.path.join(DIR_PREFIX, 'locale')
    DIR_DOCS = os.path.join(DIR_PREFIX, 'doc')
else:
    DIR_PREFIX = os.path.join(sys.prefix, 'share', 'gcentralaccess')
    DIR_LOCALE = os.path.join(sys.prefix, 'share', 'locale')
    DIR_DOCS = os.path.join(sys.prefix, 'share', 'doc', 'gcentralaccess')
# Set the paths for the folders
DIR_DATA = os.path.join(DIR_PREFIX, 'data')
DIR_UI = os.path.join(DIR_PREFIX, 'ui')
DIR_SETTINGS = BaseDirectory.save_config_path(DOMAIN_NAME)
# Set the paths for the data files
FILE_ICON = os.path.join(DIR_DATA, 'gcentralaccess.png')
FILE_CONTRIBUTORS = os.path.join(DIR_DOCS, 'contributors')
FILE_TRANSLATORS = os.path.join(DIR_DOCS, 'translators')
FILE_LICENSE = os.path.join(DIR_DOCS, 'license')
FILE_RESOURCES = os.path.join(DIR_DOCS, 'resources')
# Set the paths for configuration files
FILE_SETTINGS = os.path.join(DIR_SETTINGS, 'settings.conf')
FILE_WINDOWS_POSITION = os.path.join(DIR_SETTINGS, 'windows.conf')
FILE_SERVICES = os.path.join(DIR_SETTINGS, 'services.conf')
