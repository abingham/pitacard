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

import ConfigParser

options = {'startup': 
           {'preservegeom' : 'true',
            'usefile'      : 'custom',
            'lastfile'     : '',
            'customfile'   : '',
            'lastheight'   : '500',
            'lastwidth'    : '500',
            'lastposx'     : '380',
            'lastposy'     : '150'
            },
           
           'appearance': 
           {'rvwlastheight' : '500',
            'rvwlastwidth'  : '500',
            'rvwlastposx'   : '480',
            'rvwlastposy'   : '140'
            }
           
           }

class Config(ConfigParser.SafeConfigParser):
    def __init__(self, options):
        ConfigParser.SafeConfigParser.__init__(self)
        self.options = options

        # set defaults
        for section,values in self.options.items():
            if not self.has_section(section):
                self.add_section(section)
            for value,default in values.items():
                self.set(section, value, default)

    def read(self, filenames):
        ConfigParser.SafeConfigParser.read(self, filenames)
        
        # tear out stuff that doesn't match our options
        for section in self.sections():
            if not self.options.has_key(section):
                self.remove_section(section)
            else:
                for option in self.options[section]:
                    if not self.options[section].has_key(option):
                        self.remove_option(section, option)

def unit_test():
    print '[pitacard.config unit test]'

    errors = []

    cfg = Config(options)
    for section, values in options.items():
        for value,default in values.items():
            stored = cfg.get(section, value)
            if not default == stored:
                errors.append('Default not stored. %s:%s, %s != %s' % (section, value, default, stored))

    cfg.set('appearance', 'rvwlastposy', str(42))
    stored = cfg.getint('appearance', 'rvwlastposy')
    if stored != 42:
        error.append('Value not retrieved. %s:%s, %s != %s' % ('appearance', 'rvwlastposy', 42, stored))

    try:
        cfg.set('foo', 'bar', 'llama')
        errors.append('Failed to block setting invalid section')
    except ConfigParser.NoSectionError:
        pass

    if len(errors) == 0:
        print "PASSED"
    else:
        print "FAILED"
        for e in errors:
            print e

if __name__ == '__main__':
    unit_test()
