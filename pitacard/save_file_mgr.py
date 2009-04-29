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

import os
import gtk
import pitacard.error, pitacard.signal

class SaveFileMgr:
    OK          = 0
    ERROR       = 1
    CANCEL      = 2
    WRITE_ERROR = 3
    READ_ERROR  = 4

    def __init__(self,
                 parent_window,
                 format=None,
                 new_handler = None,
                 open_handler = None,
                 save_handler = None):
        self.parent_window = parent_window
        self.unsaved_changes = False
        self.filename = None
        self.new_handler = new_handler
        self.open_handler = open_handler
        self.save_handler = save_handler
        self.format = format
        self.change_signal = pitacard.signal.Signal()

    def flag_change(self):
        self.unsaved_changes = True
        self.change_signal()
    
    def clear_changes(self):
        self.unsaved_changes = False
        self.change_signal()

    def new(self):
        '''
        returns: cancel, error, ok
        '''
        if not self.new_handler:
            return SaveFileMgr.ERROR

        rslt = self._query_unsaved_changes()
        if not rslt == SaveFileMgr.OK:
            return rslt

        rslt = self.new_handler()
        if SaveFileMgr.OK == rslt:
            self.filename = None
            self.clear_changes()

        return rslt

    def _save(self, filename):
        if not self.save_handler:
            pitacard.error.error('no save handler set...yell at the developers!', self.parent_window)
            return SaveFileMgr.ERROR

        dir = os.path.dirname(filename)
        if os.path.lexists(filename):
            if not os.access(filename, os.W_OK):
                pitacard.error.error('%s is not writable' % filename, self.parent_window)
                return SaveFileMgr.WRITE_ERROR
        elif os.path.lexists(dir) and not os.access(dir, os.W_OK):
            pitacard.error.error('%s is not writable' % filename, self.parent_window)
            return SaveFileMgr.WRITE_ERROR

        rslt = self.save_handler(filename)
        if SaveFileMgr.OK == rslt:
            self.filename = filename
            self.unsaved_changes = False
            self.clear_changes()

        return rslt

    def save(self):
        '''
        returns: cancel, error, ok
        '''
        if not self.filename:
            return self.save_as()
        
        return self._save(self.filename)

    def save_as(self):
        '''
        returns: cancel, error, ok
        '''
        dlg = gtk.FileChooserDialog('Save as...',
                                    None,
                                    gtk.FILE_CHOOSER_ACTION_SAVE,
                                    (gtk.STOCK_CANCEL, 0,
                                     gtk.STOCK_SAVE, 1))

        rslt = SaveFileMgr.ERROR

        try:
            dlg.set_default_response(1)
            dlg.set_do_overwrite_confirmation(True)
            dlg.set_transient_for(self.parent_window)
            if self.format:
                savefilter = gtk.FileFilter()
                savefilter.add_pattern('*%s' % self.format[1]),
                savefilter.set_name(self.format[0])
                dlg.add_filter(savefilter) 
                
            while True:
                response = dlg.run()
                if 0 == response:
                    rslt = SaveFileMgr.CANCEL
                    break

                elif 1 == response:
                    fname = dlg.get_filename()
                    
                    if self.format:
                        if not fname.endswith(self.format[1]):
                            fname += self.format[1]

                    rslt = self._save(fname)
                    if SaveFileMgr.OK == rslt:
                        break
                    elif not (SaveFileMgr.CANCEL == rslt or SaveFileMgr.WRITE_ERROR == rslt):
                        break

        finally:
            dlg.destroy()

        return rslt

    def open(self, filename=None):
        '''
        returns: cancel, error, ok
        '''
        if not self.open_handler:
            pitacard.error.error('no file-open-handler', self.parent_window)
            return SaveFileMgr.ERROR

        rslt = self._query_unsaved_changes()
        if not SaveFileMgr.OK == rslt:
            return rslt
        
        if filename and not os.path.lexists(filename):
            pitacard.error.error('%s does not exist' % filename, self.parent_window)
            return SaveFileMgr.ERROR
        elif not filename:
            dlg = gtk.FileChooserDialog('Open',
                                        None,
                                        gtk.FILE_CHOOSER_ACTION_OPEN,
                                        (gtk.STOCK_CANCEL,
                                         gtk.RESPONSE_CANCEL,
                                         gtk.STOCK_OPEN,
                                         gtk.RESPONSE_OK))
            if self.format:
                filter = gtk.FileFilter()
                filter.add_pattern('*%s' % self.format[1])
                dlg.set_filter(filter)

            dlg.set_transient_for(self.parent_window)
            rslt = dlg.run()
            filename = dlg.get_filename()
            dlg.destroy()
            
            if gtk.RESPONSE_CANCEL == rslt:
                return SaveFileMgr.CANCEL

        if not os.access(filename, os.R_OK):
            pitacard.error.error('%s is not readable' % filename, self.parent_window)
            return SaveFilemgr.ERROR

        rslt = self.open_handler(filename)
        if SaveFileMgr.OK == rslt:
            self.filename = filename
            self.clear_changes()
        return rslt

    def _query_unsaved_changes(self):
        '''
        Checks to see if there are unsaved changes and, if so, gives the user
        the opportunity to save them. This is intended to be called in response
        to operations that replace the existing data with new data (i.e. open,
        new, etc.).

        If this returns CANCEL, then the user has elected to cancel the operation
        that would replace the current data. If it returns OK, then either the
        user saved the changes or elected to not save them...in either case, the
        pending operation should proceed.

        A return value of ERROR indicates that an error occurred in saving the
        changes. You should probably not continue with the pending operation, but
        that's up to you.
        '''
        if not self.unsaved_changes:
            return SaveFileMgr.OK

        dlg = gtk.MessageDialog(None,
                                False,
                                gtk.MESSAGE_QUESTION,
                                gtk.BUTTONS_NONE, # gtk.BUTTONS_YES_NO | gtk.BUTTONS_CANCEL,
                                'Save unsaved changes?')
        dlg.add_buttons(gtk.STOCK_YES,    gtk.RESPONSE_YES, 
                        gtk.STOCK_NO,     gtk.RESPONSE_NO,
                        gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)

        dlg.set_transient_for(self.parent_window)
        rslt = dlg.run()
        dlg.destroy()
        if gtk.RESPONSE_NO == rslt:
            return SaveFileMgr.OK
        elif gtk.RESPONSE_CANCEL == rslt:
            return SaveFileMgr.CANCEL
        
        return self.save()

    def quit(self):
        return self._query_unsaved_changes()
