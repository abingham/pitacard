# pitacard: A Leitner-method flashcard program
# Copyright (C) 2006 Austin Bingham
#
# This program is free software# you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation# either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY# without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program# if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# You can reach the author at:
#     austin.bingham@gmail.com

import gtk

class SaveFileMgr:
    OK     = 1
    ERROR  = 2
    CANCEL = 3

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
        return rslt

    def save(self):
        if not self.filename:
            return self.save_as()
        return self._save()
        
    def save_as(self):
        dlg = gtk.FileChooserDialog('Save as...',
                                    None,
                                    gtk.FILE_CHOOSER_ACTION_SAVE,
                                    (gtk.STOCK_CANCEL,
                                     gtk.RESPONSE_CANCEL,
                                     gtk.STOCK_OPEN,
                                     gtk.RESPONSE_OK))
        response = dlg.run()
        filename = dlg.get_filename()
        dlg.destroy()
        if response == gtk.RESPONSE_CANCEL:
            return SaveFileMgr.CANCEL
        self.filename = filename
        return self._save()

    def query_unsaved_changes(self):
        if not self.unsaved_changes:
            return SaveFileMgr.OK
        dlg = gtk.MessageDialog(None,
                                False,
                                gtk.MESSAGE_QUESTION,
                                gtk.BUTTONS_YES_NO,
                                'Save unsaved changes?')
        rslt = dlg.run()
        dlg.destroy()
        if rslt == gtk.RESPONSE_NO:
            return SaveFileMgr.OK
        return self.save()

    def open(self, filename=None):
        rslt = self.query_unsaved_changes()
        if not rslt == SaveFileMgr.OK:
            return rslt

        if not filename:
            dlg = gtk.FileChooserDialog('Open',
                                        None,
                                        gtk.FILE_CHOOSER_ACTION_OPEN,
                                        (gtk.STOCK_CANCEL,
                                         gtk.RESPONSE_CANCEL,
                                         gtk.STOCK_OPEN,
                                         gtk.RESPONSE_OK))
            rslt = dlg.run()
            filename = dlg.get_filename()
            dlg.destroy()

            if rslt == gtk.RESPONSE_CANCEL:
                return SaveFileMgr.CANCEL
            
        rslt = self.open_impl(filename)
        if rslt == SaveFileMgr.OK:
            self.clear_changes()
            self.filename = filename
        return rslt

    def quit(self):
        rslt = self.query_unsaved_changes()
        if not rslt == SaveFileMgr.OK:
            return rslt
        gtk.main_quit()
