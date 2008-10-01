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

from os import access, path
from string import lower
from copy import deepcopy
import shutil
import gtk
from ConfigParser import *

class ConfigTool(SafeConfigParser):
    '''Handles all management, reading, and writing to of config file.

    The handling of configuration in pitacard has three distinct, obvious phases: startup, concurrent, and end.

    When pitacard is opened
        1. The config FILE is checked for permissions.
        2. If it can be read, the data in the file is parsed by and into this class.
        3. The data is sifted for valid sections and options. Invalid sections are not kept in memory and are thus cleaned from the file when the file is next written. I consider invalid sections outstanding enough to remove, but to go through each option in the config file and check it each time pitacard is started feels like an eternal waste of processor for an occasional action that'll barely ever be of use.

    During the use of the app:
        1. When it is necessary to read data from the parser, this CLASS' read function is called for data under a certain option.
            The read function checks for the existence of both the section and the option.
                a.If the option (or its entire section) does not exist, the value None is returned.
                b.If the section and option does exist, its value is returned.
        2. When it is necessary to write data to the parser, this CLASS' write function is called for data under a certain option.
            The write function whether the section is valid, and then checks for the existance of the section.
                a.If the section does not exist, the section is created.
                b.If the section is not valid, it is not written to.
            The passed option is then set to the passed value within that section.
        There are multiple aspects of the functions that allow for multiple options and sections to be addressed at once, but they all use the above basic functions.

        After the app is ended:
            1. The config FILE is checked for permissions again.
            2.a. If the user has write access to FILE, the PARSER rewrites the configfile.
            2.b. If not, nothing happens. A warning is given to the effect that config wasn't written.'''

    valid_config = {'startup': [
                        # these are enforced options. Options that are
                        # not recognized will not be deleted. Not just
                        # out of courtesy, but because it can be
                        # useful but options which are known to exist
                        # are created if non-existant, given a default
                        # value when created if possible, option's
                        # name, default value, possible values
                        ('preservegeom', 'true', ['true', 'false']),
                        ('usefile', 'custom', ['none', 'last', 'custom']),
                        ('lastfile', ''),
                        ('customfile', ''),
                        ('lastheight', '500', int),
                        ('lastwidth', '500', int),
                        ('lastposx', '380', int),
                        ('lastposy', '150', int)
                        ],
                    'appearance': [
                        ('rvwlastheight', '500', int),
                        ('rvwlastwidth', '500', int),
                        ('rvwlastposx', '480', int),
                        ('rvwlastposy', '140', int)
                        ]
                    }

    def __init__(self, configfile):
        SafeConfigParser.__init__(self)
        self.configfile = configfile
        self.loadconfig()

    def loadconfig(self):
        '''for getting the data from the config file to the parser'''
        permissions, errormessage = self.checkpermissions(self.configfile, True)
        errorbox = gtk.MessageDialog(None,
                            False,
                            gtk.MESSAGE_ERROR,
                            gtk.BUTTONS_NONE,
                            errormessage)
        if 'r' in permissions:
            try:
                self.read(self.configfile)
            except:
                if access(str(self.configfile+'_backup'), 0):
                    try:
                        self.read(str(self.configfile+'_backup'))
                        backupread = True
                    except:
                        backupread = False
                        errormessage = str("WARNING! The pitacard configfile " + self.configfile + " is corrupt, meaning someone has probably manually editted it, in which case you should delete it, or it's not a configfile, in which case you should use a different file path. The backup configfile was also corrupt.")
                        print errormessage

                    if backupread == True:
                        try:
                            shutil.copy(str(self.configfile+'_backup'), self.configfile)
                            errormessage = str("WARNING! The pitacard configfile " + self.configfile + " is corrupt. Pitacard has replaced its data with the data in the backup configfile.")
                            print errormessage
                        except:
                            errormessage = str("WARNING! The pitacard configfile " + self.configfile + " is corrupt, meaning someone has probably manually editted it, in which case you should delete it, or it's not a configfile, in which case you should use a different file path. The original configfile isn't writable by you, which means you probably don't have permission to delete it.")
                            print errormessage
                else:
                    errormessage = str("WARNING! The pitacard configfile " + self.configfile + " is corrupt, meaning someone has probably manually editted it, in which case you should delete it, or it's not a configfile, in which case you should use a different file path. No backup file existed.")
                    print errormessage


        else:
            print str("WARNING! " + errormessage)
        for section in self.sections():
            if not section in ConfigTool.valid_config:
                self.remove_section(section)
        for section in ConfigTool.valid_config:
            if not self.has_section(section):
                self.add_section(section)
            for option in ConfigTool.valid_config[section]:
                if not self.has_option(section, option[0]):
                        self.set(section, option[0], option[1])
                if len(option) >= 3:
                    if type(option[2]) == type:
                        try:
                            type(option[2](self.get(section, option[0]))) == option[2]
                        except:
                            self.set(section, option[0], option[1])
                    else:
                        if not self.get(section, option[0]) in option[2]:
                            self.set(section, option[0], option[1])
        self.saveconfig(str(self.configfile+'_backup'), False)

    def readvalue(self, section='*', option='*'):
        '''Reads value(s) from the parser, returns value.
        If section == '*', irrelevant of what option is, all options from every section are returned in the form of dictionaries within a master dictionary. Such as:
        {'Clothes': {'shirt': 'blue', 'pants': 'red', 'socks': 'purple'}, 'House': {'walls': 'turquoise', 'roof': 'fuschia'}}
        If section is absolute and option == '*', all options and their corresponding values from the section are returned in the form of a dictionary, such as:
        {'shirt': 'blue', 'pants': 'red', 'socks': 'purple' }
        if sectiona and option are absolute, only the value of the option is returned.'''
        if section == '*':
            optionsdict = {}
            for section in self.sections():
               optionsdict[section] = {}
               for option in self.options(section):
                   optionsdict[section][option] = self.get(section, option)
            return optionsdict
        elif self.has_section(section):
           if option == '*':
               optionsdict = {}
               for option in self.options(section):
                   optionsdict[option] = self.get(section, option)
               return optionsdict
           elif self.has_option(section, option):
                   return self.get(section, option)
        return ''

    def writevalue(self, valuedict):
        '''Writes a value to the parser

        Unlike with readvalue, you assign location with a dictionary here. For example
        self.writevalue({'Clothes':{'shirt':'blue', 'pants':'red'}}),
        this allows for more flexible and expandable value assignment.
        However, in readvalue, that kind of complexity is unecessary.'''
        if type(valuedict) == dict:
            for section in valuedict:
                if section in ConfigTool.valid_config and type(valuedict[section]) == dict:
                    if not self.has_section(section):
                        self.add_section(section)
                    for option in valuedict[section]:
                        if valuedict[section][option] == None:
                            valuedict[section][option] = ''
                        if valuedict[section][option] == 'del':
                            print 'Trying to delete ' + str(section) + ' : ' + str(option)
                            self.remove_option(section, option)
                        else:
                            self.set(section, option, str(valuedict[section][option]))
                else:
                    print "Error! Either", section, "is not a valid config section name, or the options and values you gave as it's value were not in the form of a dictionary!"
                    return None
            return True
        return None

    def saveconfig(self, configfile='default', verbose=True):
        '''for getting the data from the parser to the config file'''
        if configfile == 'default':
            configfile = self.configfile
        permissions = self.checkpermissions(configfile, False)
        if 'r+' in permissions:
            cfgobj = open(configfile, 'r+')
            self.write(cfgobj)
        return True

    def checkpermissions(self, configfile, verbose=False):
        '''first of all, let's get all file-existing and permissions testing out of the way before we try to use a config file.'''
        if not access(configfile, 0):
            '''If the file doesn't exist'''
            error = str('Config file ' + configfile + ' does not exist... ')
            configdir = path.dirname(configfile)
            if not access(configdir, 6):
                error = str(' Cannot create config file - You do not have Read/Write access to its location.')
                permissions = ''
            else:
                try:
                    open(configfile, 'w').close()
                    error = error + str('Successfully created Config file at ' + configfile)
                    permissions = 'r+'
                except:
                    error = error + str('Could not create configfile for some reason.')
                    permissions = ''
        elif not access(configfile, 4):
            '''if the file exists but can't be read'''
            error = str(' You do not have Read access to Config file ' + configfile + "\nYou will not have access to previous configurations (such as favorites, etc.)")
            permissions = ''
        elif not access(configfile, 6):
            '''if the file exists, can be read, but can't be written to.'''
            error = str(' You have Read access but no Write access to Config file ' + configfile + "\nAny changes in configuration (favorites, etc.) will not be saved.")
            permissions = 'r'
        else:
            '''if the file exists, can be read, and can be written to.'''
            error = ('Config file successfully loaded.')
            permissions = 'r+'
        if verbose==True:
            return permissions, error
        else:
            return permissions

class StartupSettings:
    '''this is very integrated with the parent app and uses the open
    tool, config instance, gladefile, and window of the given parent
    UI instance. If the UI is fundamentally changed in any of these,
    this part probably needs to be changed. Don't worry, all variable
    grabbing from the parent is done in the first few lines. If
    necessary, all of these variables might be stretched as a long
    list of arguments, but it seems a bit excessive. This class
    already makes assumptions about the parent, and to pretend it is
    modular is pointless. The only possible value is to have the
    variables being used cosolidated on the pitacard.py script.'''
    def __init__(self, parent):
        self.config = parent.config
        self.cfgtemp = deepcopy(self.config)
        self.gladefile = parent.gladefile
        lowerstr = (lambda x: lower(str(x)))

        xml = gtk.glade.XML(self.gladefile, 'ConfigDlg')
        self.window = xml.get_widget('ConfigDlg')
        self.window.set_transient_for(parent.main_window)

        self.window.preservegeom = xml.get_widget('Config - WindowGeom')
        self.window.usefilenone = xml.get_widget('Config - Usefile - None')
        self.window.usefilelast = xml.get_widget('Config - Usefile - Last')
        self.window.usefilecust = xml.get_widget('Config - Usefile - Custom')
        self.window.custfile_entry = xml.get_widget('Config - CustomFile - Entry')
        self.window.custfile_selector = xml.get_widget('Config - CustomFile - Select')
        self.window.custfile_warn = xml.get_widget('Config - Cust - Testvalid')
        self.window.okay = xml.get_widget('Config - Okay')
        self.window.cancel = xml.get_widget('Config - Cancel')

        self.window.preservegeom.connect('toggled', lambda w: self.cfgtemp.writevalue({'startup': {'preservegeom':  lowerstr(self.window.preservegeom.get_active())}}))
        self.window.usefilenone.connect('pressed', lambda w: self.set_usefile('none'))
        self.window.usefilelast.connect('pressed', lambda w: self.set_usefile('last'))
        self.window.usefilecust.connect('pressed', lambda w: self.set_usefile('custom'))
        self.window.custfile_entry.connect('changed', lambda w: self.checkvalid())
        self.window.custfile_selector.connect('clicked', lambda w: self.selector())
        self.window.okay.connect('clicked', lambda w: self.close(True))
        self.window.cancel.connect('clicked', lambda w: self.close(False))

        self.loadconf()
        self.checkvalid()

    def loadconf(self):
        preservegeom = lower(self.cfgtemp.readvalue('startup', 'preservegeom'))
        if preservegeom == 'true':
            self.window.preservegeom.set_active(True)
        elif preservegeom == 'false':
            self.window.preservegeom.set_active(False)

        usefile = lower(self.cfgtemp.readvalue('startup', 'usefile'))
        if usefile == 'none':
            self.window.usefilenone.set_active(True)
        elif usefile == 'last':
            self.window.usefilelast.set_active(True)
        elif usefile == 'custom':
            self.window.usefilecust.set_active(True)
            self.window.custfile_warn.set_property('visible', True)
            self.window.custfile_selector.set_property('sensitive', True)
            self.window.custfile_entry.set_property('sensitive', True)

        customfile = self.cfgtemp.readvalue('startup', 'customfile')
        print customfile
        self.window.custfile_entry.set_text(customfile)

    def set_usefile(self, selection):
        if selection == 'custom':
            self.window.custfile_warn.set_property('visible', True)
            self.window.custfile_selector.set_property('sensitive', True)
            self.window.custfile_entry.set_property('sensitive', True)
        else:
            self.window.custfile_warn.set_property('visible', False)
            self.window.custfile_selector.set_property('sensitive', False)
            self.window.custfile_entry.set_property('sensitive', False)
        self.cfgtemp.writevalue({'startup': {'usefile':  selection}})

    def selector(self):
        # getpath = self.open(None, False)
        dlg = gtk.FileChooserDialog('Open',
                                    None,
                                    gtk.FILE_CHOOSER_ACTION_OPEN,
                                    (gtk.STOCK_CANCEL,
                                     gtk.RESPONSE_CANCEL,
                                     gtk.STOCK_OK,
                                     gtk.RESPONSE_OK))
            
        dlg.set_transient_for(self.window)
        rslt = dlg.run()
        filename = dlg.get_filename()
        dlg.destroy()

        if gtk.RESPONSE_OK == rslt:
            self.window.custfile_entry.set_text(filename)

    def checkvalid(self):
        givenpath = self.window.custfile_entry.get_text()
        if givenpath == '':
            self.window.custfile_warn.set_markup('<span foreground="#FF0000">Please enter the location of a card file.</span>')
        elif not access(givenpath, 0):
            self.window.custfile_warn.set_markup('<span foreground="#FF0000">Warning! file does not exist!</span>')
        elif not access(givenpath, 4):
            self.window.custfile_warn.set_markup('<span foreground="#FF0000">Warning! you do not have permission to read that file!</span>')
        else:
            self.window.custfile_warn.set_markup('File exists.')
        self.cfgtemp.writevalue({'startup': {'customfile':  givenpath}})

    def close(self, bool):
        if bool == True:
            for section in self.cfgtemp.sections():
                for option in self.cfgtemp.options(section):
                    self.config.set(section, option, self.cfgtemp.get(section, option))
        self.window.destroy()
        del self
