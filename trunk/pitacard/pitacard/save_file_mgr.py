# pitacard: A Leitner-method flashcard program
# Copyright (C) 2006 Austin Bingham, Nate Ross
#
# This program is free software# you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation# either version 2
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

import gtk, re
from os import path
import error

class SaveFileMgr:
    OK     = 1
    ERROR  = 2
    CANCEL = 3
    saveformats = [     #This is in the form of a list and tuples instead of a dictionary because dictionaries can't be ordered. We need to have formats which take preference.
    ('stack', '.stack'),
    ('csv', '.csv'),
    ('csv (compatibility mode)', '.csv') ]    #values are actual file extension. keys are descriptions and identifiers.

    def __init__(self):
        self.unsaved_changes = False
        self.filename = None

    def flag_change(self):
        self.unsaved_changes = True

    def clear_changes(self):
        self.unsaved_changes = False

    def _save(self):
        assert self.filename, 'Filename not set in _save'
        rslt = self.save_impl(self.filename)
        if rslt == SaveFileMgr.OK:
            self.clear_changes()
        #return rslt

    def save(self):
        if not self.filename:
            return self.save_as()
        return self._save()


    def save_as(self):
        def writeconfirm(parent):
            '''Makes dialog asking if the user wants to overwrite an existing file. Returns True/False.'''
            ask_overwrite = gtk.MessageDialog(None,
                                    False,
                                    gtk.MESSAGE_QUESTION,
                                    gtk.BUTTONS_NONE,
                                    'File exists. Overwrite?')
	    ask_overwrite.add_buttons("Yes", 1, "No", 0)
            ask_overwrite.set_default_response(0)
            ask_overwrite.set_transient_for(parent)
            overwrite_rslt = ask_overwrite.run()
            if overwrite_rslt == 1:
                ask_overwrite.destroy()
                return True
            elif overwrite_rslt == 0:
                ask_overwrite.destroy()
		return False

        def checkname(dialog):
            '''Checks for file extension. If nonexistant, adds it. Checks the end result filename against existing files. If a file is present, give the overwrite dialog.'''
            filename = dialog.get_filename()
            if filename == None:
                return 0

            #PART 1: CHECKING AND (POSSIBLY) ADDING TO EXTENSIONS
            for i in SaveFileMgr.saveformats:
                if re.search('' + i[1] + '\Z', filename):
                        '''if the user has appended a valid file extension to the name of the file, ignore the selected format and just use that format and name.'''
                        self.filename = filename
                        self.saveformat = i[0] #note that this isn't the actual extension, but the descriptor.
			break
            if self.filename != filename:
                '''if the user has not appended a valid file extension to the name of the file, use the selected file format, and append its extension to the end of the given name.'''
                selectedformat = dialog.get_filter()   #Gets the currently selected filter.
                selectedformat = selectedformat.get_name()
                #below is a oneliner way to find and append the appropriate file extension using the format descriptor. For example 'csv (compatibility mode)' would fetch .csv ... It's a crufty hack, but I'm resistant to establish a "system" of format descriptor strings just to allow string manipulation to find the actual file extension from the descriptor string. Using tuples are fine by me.
                self.filename = filename + SaveFileMgr.saveformats[[ x.__contains__(selectedformat) for x in SaveFileMgr.saveformats ].index(True)][1]
                self.saveformat = selectedformat #note that this isn't the actual extension, but the descriptor.

            #PART 2: TEST IF FILE EXISTS, IF SO, MAKE OVERWRITE DIALOG
	    if path.lexists(self.filename):
                if writeconfirm(dialog):
		    '''if that file already exists, ask if they want to overwrite it. If they do...'''
		    if error.cant_access(self.filename, 2, dialog):
		        '''check whether they can write to the folder. If they can't, say so.'''
		        return 0
                    dialog.destroy()
                    return 1
		else:
		    return 0
	    else:
		'''if the file does not exist, try to save it. Test whether you can write to it's base directory or not.'''
		self.filedir = path.dirname(self.filename)
		if error.cant_access(self.filedir, 2, dlg):
		   '''check whether they can write to the folder. If they can't, say so.'''
		   return 0
                dialog.destroy()
                return 1

        #CREATE SAVE DIALOG
        dlg = gtk.FileChooserDialog('Save as...',
                                    None,
                                    gtk.FILE_CHOOSER_ACTION_SAVE,
                                    (gtk.STOCK_CANCEL, 0,
                                     gtk.STOCK_SAVE, 1))
        dlg.set_default_response(1)
        dlg.set_do_overwrite_confirmation(False)
        dlg.set_transient_for(self.main_window)

        #CREATE SAVE FILTERS.
        for d in [ x[0] for x in self.saveformats ]:
	    '''create filechooser filters. This creates the combobox by which a user can select which format to save in.
            All files with valid formats are viewed, no matter what format is selected in the combobox
            If the submitted filename does not have a valid extension on it, the selected format in the format combo-box is used.'''
	    savefilter = gtk.FileFilter()
	    for ext in [ x[1] for x in self.saveformats ]:
		'''this (repeatedly constructing the patterns for each instance of a filter) is an obvious bottleneck, but I'm not quite sure how to remedy it. I haven't found any way to copy the patterns of another filter. Probably not that much of a problem, but still... it bugs me.'''
                savefilter.add_pattern('*' + ext)
            savefilter.set_name(d)
            dlg.add_filter(savefilter)

        #RUN THE SAVE DIALOG
        while 1==1:
            response = dlg.run()
            if response == 0:
                dlg.destroy()
                return SaveFileMgr.CANCEL
                break
            if response == 1:
                save_rslts = checkname(dlg)
                if save_rslts == True:
		    self._save()
                    '''if the user decided to save instead of say, canceling when an overwrite dialog came up, end the loop.'''
                    break


    def query_unsaved_changes(self):
        if not self.unsaved_changes:
            return SaveFileMgr.OK
        dlg = gtk.MessageDialog(None,
                                False,
                                gtk.MESSAGE_QUESTION,
                                gtk.BUTTONS_YES_NO,
                                'Save unsaved changes?')
        dlg.set_transient_for(self.main_window)
        rslt = dlg.run()
        dlg.destroy()
        if rslt == gtk.RESPONSE_NO:
            return SaveFileMgr.OK
        return self.save()


    def new(self, filename=None):
        rslt = self.query_unsaved_changes()
        if not rslt == SaveFileMgr.OK:
            return rslt

        rslt = self.new_impl()
        self.filename = None
        return rslt

    def open(self, filename=None, realopen=True):
        #realopen - True opens file, False just returns path.
        rslt = self.query_unsaved_changes()
        if not rslt == SaveFileMgr.OK:
            return rslt

        if filename and not path.lexists(filename):
            print "File does not exist! If you moved it, you'll need to use it's new path instead."
            return SaveFileMgr.ERROR
        elif not filename:
            dlg = gtk.FileChooserDialog('Open',
                                        None,
                                        gtk.FILE_CHOOSER_ACTION_OPEN,
                                        (gtk.STOCK_CANCEL,
                                         gtk.RESPONSE_CANCEL,
                                         gtk.STOCK_OPEN,
                                         gtk.RESPONSE_OK))
            openfilter = gtk.FileFilter()
	    for i in SaveFileMgr.saveformats:
            	openfilter.add_pattern('*' + i[1])
            dlg.set_filter(openfilter)
            dlg.set_transient_for(self.main_window)
            rslt = dlg.run()
            filename = dlg.get_filename()
            dlg.destroy()

        if rslt == gtk.RESPONSE_CANCEL:
                return SaveFileMgr.CANCEL

        #check for valid file extension
        for i in SaveFileMgr.saveformats:
            if re.search('' + i[1] + '\Z', filename):
                self.saveformat = i[0]
                break
        else:
            print "Error! File extension not recognized!"
            return SaveFileMgr.ERROR

        if realopen == True:
            rslt = self.open_impl(filename)
            if rslt == SaveFileMgr.OK:
                self.clear_changes()
                self.filename = filename
            return rslt
        elif realopen == False:
            return filename

    def quit(self):
        rslt = self.query_unsaved_changes()
        if not rslt == SaveFileMgr.OK:
            return rslt
        width, height = self.main_window.get_size()
        posx, posy = self.main_window.get_position()
        self.config.writevalue({'startup': {'lastfile': self.filename}})
        self.config.writevalue({'startup': {'lastwidth': width}})
        self.config.writevalue({'startup': {'lastheight': height}})
        self.config.writevalue({'startup': {'lastposx': posx}})
        self.config.writevalue({'startup': {'lastposy': posy}})
        rslt = self.config.saveconfig()
        if rslt == True:
            self.main_window.destroy()
            gtk.main_quit()