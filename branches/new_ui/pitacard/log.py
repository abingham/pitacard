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

import logging, logging.handlers, os.path

def init_logging(file=None,
                 file_level=logging.WARNING,
                 screen_level=logging.WARNING):
    if file:
        logfile = logging.handlers.RotatingFileHandler(os.path.expanduser(file),
                                                       maxBytes=10000,
                                                       backupCount=1)
        logfile.setLevel(file_level)
        formatter = logging.Formatter('%(asctime)s %(name)-12s: %(levelname)-8s %(message)s')
        logfile.setFormatter(formatter)
        logging.getLogger('').addHandler(logfile)
        logging.getLogger('').setLevel(logging.DEBUG)

    # This makes sure all ERROR messages are printed to screen
    to_screen = logging.StreamHandler()
    to_screen.setLevel(screen_level)
    logging.getLogger('').addHandler(to_screen)
