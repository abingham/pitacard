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
import logging, optparse, os, string
import config, log, ui

logger = logging.getLogger('pitacard.main')

def parse_args():
    parser = optparse.OptionParser()
    parser.add_option("-f", "--file", dest="filename",
                      help="log file to load at startup", metavar="FILE")
    parser.add_option("-c", "--config-file", dest="configfile",
                      help="config file", metavar="FILE",
                      default=os.path.expanduser(os.path.join('~', '.pitacardrc')))
    return parser.parse_args()

def init_config(config_files):
    cfg = config.Config(config.options)
    cfg.read(config_files)
    return cfg

def main(dev=False):
    log.init_logging()

    (options, args) = parse_args()

    if not os.path.lexists(options.configfile):
        logger.error('Unable to open config file: %s' % options.configfile)
    cfg = init_config([options.configfile])

    m = ui.UI(os.path.join(os.path.dirname(__file__),
                           'glade',
                           'pitacard.glade'),
              cfg)

    filename = ''
    if options.filename:
        filename = options.filename
    elif cfg.get('startup', 'usefile').lower() == 'custom':
        filename = cfg.get('startup', 'customfile')
    elif cfg.get('startup', 'usefile').lower() == 'last':
        filename = cfg.get('startup', 'lastfile')

    filename = os.path.expanduser(filename)

    if filename:
        if not os.path.lexists(filename):
            logger.warning('Could not open startup stack: %s' % filename)
        else:
            logger.info('Opening file: %s' % filename)
            m.open(filename)

    gtk.main()

    # write config
    cfgfile = open(options.configfile, 'w')
    if not cfgfile:
        logger.error('Unable to open config file for writing: %s' % options.configfile)
    else:
        logger.info('Reading config file: %s' % cfgfile)
        cfg.write(cfgfile)

if __name__ == '__main__':
    main()
