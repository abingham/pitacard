# pitacard: A Leitner-method flashcard program
# Copyright (C) 2006-2008 Austin Bingham, Nate Ross
#
# This program is free software you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; see the file LICENSE. If not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# You can reach the authors at:
#     austin.bingham@gmail.com
#     teal@mailshack.com

import gtk
from os import access

def error(msg, parent):
    dlg = gtk.MessageDialog(None,
                            False,
                            gtk.MESSAGE_ERROR,
                            gtk.BUTTONS_CLOSE,
                            msg)
    dlg.set_transient_for(parent)
    dlg.run()
    dlg.destroy()

def warning(msg, parent):
    dlg = gtk.MessageDialog(None,
                            False,
                            gtk.MESSAGE_WARNING,
                            gtk.BUTTONS_CLOSE,
                            msg)
    dlg.set_transient_for(parent)
    dlg.run()
    dlg.destroy()
