# -*- coding: utf-8 -*-
#
# Copyright (C) 2007-2009 Andrew Resch <andrewresch@gmail.com>
#
# This file is part of Deluge and is licensed under GNU General Public License 3.0, or later, with
# the additional special exception to link portions of this program with the OpenSSL library.
# See LICENSE for more details.
#

from __future__ import unicode_literals

import logging

from deluge.ui.ui import UI

log = logging.getLogger(__name__)


# Keep this class in __init__.py to avoid the console having to import everything in gtkui.py
class Gtk(UI):

    cmd_description = """GTK-based graphical user interface"""

    def __init__(self, *args, **kwargs):
        super(Gtk, self).__init__('gtk', *args, description='Starts the Deluge GTK+ interface', **kwargs)

        group = self.parser.add_argument_group(_('GTK Options'))
        group.add_argument(
            'torrents',
            metavar='<torrent>',
            nargs='*',
            default=None,
            help=_(
                'Add one or more torrent files, torrent URLs or magnet URIs'
                ' to a currently running Deluge GTK instance',
            ),
        )

    def start(self):
        super(Gtk, self).start()
        from deluge.ui.gtkui.gtkui import GtkUI
        import deluge.common

        def run(options):
            try:
                gtkui = GtkUI(options)
                gtkui.start()
            except Exception as ex:
                log.exception(ex)
                raise

        deluge.common.run_profiled(
            run,
            self.options,
            output_file=self.options.profile,
            do_profile=self.options.profile,
        )


def start():
    Gtk().start()
