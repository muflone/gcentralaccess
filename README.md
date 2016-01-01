gCentralAccess
==============
**Description:** Manage external resources from a centralized management
console.

**Copyright:** 2015-2016 Fabio Castelli (Muflone) <muflone(at)vbsimple.net>

**License:** GPL-2+

**Codice sorgente:** https://github.com/muflone/gcentralaccess

**Documentazione:** http://www.muflone.com/gcentralaccess/

System Requirements
-------------------

* Python 2.x (developed and tested for Python 2.7.5)
* GTK+ 3.0 libraries for Python 2.x
* GObject libraries for Python 2.x
* XDG library for Python 2.x
* Distutils library for Python 2.x (usually shipped with Python distribution)

Installation
------------

A distutils installation script is available to install from the sources.

To install in your system please use:

    cd /path/to/folder
    python2 setup.py install

To install the files in another path instead of the standard /usr prefix use:

    cd /path/to/folder
    python2 setup.py install --root NEW_PATH

Usage
-----

If the application is not installed please use:

    cd /path/to/folder
    python2 gcentralaccess.py

If the application was installed simply use the gcentralaccess command.
