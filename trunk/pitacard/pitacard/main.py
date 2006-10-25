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

import optparse, os, string
import configmanage
from pitacard import *

def parse_args():
    parser = optparse.OptionParser()
    parser.add_option("-f", "--file", dest="filename",
                      help="log file to load at startup", metavar="FILE")
    parser.add_option("-c", "--config-file", dest="configfile",
                      help="config file", metavar="FILE",
                      default=os.path.expanduser(os.path.join('~', '.pitacardrc')))
    return parser.parse_args()

def main(dev=False):
    (options, args) = parse_args()

    config = configmanage.ConfigTool(options.configfile)

    m = UI(os.path.join(os.path.dirname(__file__),
                        'glade',
                        'pitacard.glade'),
           config)

    filename = ''
    if options.filename:
        filename = options.filename
    elif string.lower(str(config.readvalue('startup', 'usefile'))) == 'custom':
        if os.path.lexists(config.readvalue('startup', 'customfile')):
            filename = config.readvalue('startup', 'customfile')
        elif config.readvalue('startup', 'customfile') != "":
            print "Note: Could not open startup stack", config.readvalue('startup', 'customfile')
    elif string.lower(str(config.readvalue('startup', 'usefile'))) == 'last' and os.path.lexists(config.readvalue('startup', 'lastfile')):
        filename = config.readvalue('startup', 'lastfile')

    filename = os.path.expanduser(filename)

    if filename:
        print 'Opening file:',filename
        m.open(filename)
    gtk.main()

if __name__ == '__main__':
    main()
