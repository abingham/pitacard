# pitacard: A Leitner-method flashcard program
# Copyright (C) 2006 Austin Bingham, Nate Ross
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

#!/usr/bin/env python
import gtk

from kiwi.ui.gadgets import quit_if_last
from kiwi.ui.delegates import GladeDelegate
from kiwi.ui.objectlist import Column

class MainWindow(GladeDelegate):
    def __init__(self):
        GladeDelegate.__init__(self,
                               gladefile="main_window",
                               delete_handler=quit_if_last)
        #self.card_list.set_columns([Column('front', 'Front'),
        #                            Column('back', 'Back')])

    def on_file_open__activate(self, button):
        print 'open clicked'


if __name__ == '__main__':
    app = MainWindow()
    app.show()
    gtk.main()
