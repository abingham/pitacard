import os
import gtk
import error

class SaveFileMgr:
    OK          = 0
    ERROR       = 1
    CANCEL      = 2
    WRITE_ERROR = 3
    READ_ERROR  = 4

    def __init__(self,
                 parent_window,
                 new_handler = None,
                 open_handler = None,
                 save_handler = None):
        self.parent_window = parent_window
        self.unsaved_changes = False
        self.filename = None
        self.new_handler = new_handler
        self.open_handler = open_handler
        self.save_handler = save_handler
        self.formats = []

    def add_format(self, name, suffix, id):
        self.formats.append((name, suffix, id))

    def flag_change(self):
        self.unsaved_changes = True
    
    def clear_changes(self):
        self.unsaved_changes = False

    def new(self):
        '''
        returns: cancel, error, ok
        '''
        if not self.new_handler:
            return SaveFileMgr.ERROR

        rslt = self._query_unsaved_changes()
        if not rslt == SaveFileMgr.OK:
            return rslt

        return self.new_handler()

    def _save(self, filename):
        if not self.save_handler:
            error.error('no save handler set...yell at the developers!', self.parent_window)
            return SaveFileMgr.ERROR

        dir = os.path.dirname(filename)
        if os.path.lexists(filename):
            if not os.access(filename, os.W_OK):
                error.error('%s is not writable' % filename, self.parent_window)
                return SaveFileMgr.WRITE_ERROR
        elif os.path.lexists(dir) and not os.access(dir, os.W_OK):
            error.error('%s is not writable' % filename, self.parent_window)
            return SaveFileMgr.WRITE_ERROR

        rslt = self.save_handler(filename)
        if SaveFileMgr.OK == rslt:
            self.filename = filename
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
            for format in self.formats:
                savefilter = gtk.FileFilter()
                savefilter.add_pattern('*%s' % format[1]),
                savefilter.set_name(format[0])
                dlg.add_filter(savefilter) 
                
            while True:
                response = dlg.run()
                if 0 == response:
                    rslt = SaveFileMgr.CANCEL
                    break
                if 1 == response:
                    fname = dlg.get_filename()
                    if not fname.endswith('.pitacard'):
                        fname += '.pitacard'
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
            error.error('no file-open-handler', self.parent_window)
            return SaveFileMgr.ERROR

        rslt = self._query_unsaved_changes()
        if not SaveFileMgr.OK == rslt:
            return rslt
        
        if filename and not path.lexists(filename):
            error.error('%s does not exist' % filename, self.parent_window)
            return SaveFileMgr.ERROR
        elif not filename:
            dlg = gtk.FileChooserDialog('Open',
                                        None,
                                        gtk.FILE_CHOOSER_ACTION_OPEN,
                                        (gtk.STOCK_CANCEL,
                                         gtk.RESPONSE_CANCEL,
                                         gtk.STOCK_OPEN,
                                         gtk.RESPONSE_OK))
            filter = gtk.FileFilter()
            for f in self.formats:
                filter.add_pattern('*%s' % f[1])
            dlg.set_filter(filter)
            dlg.set_transient_for(self.parent_window)
            rslt = dlg.run()
            filename = dlg.get_filename()
            dlg.destroy()
            
            if gtk.RESPONSE_CANCEL == rslt:
                return SaveFileMgr.CANCEL

        if not os.access(filename, os.R_OK):
            error.error('%s is not readable' % filename, self.parent_window)
            return SaveFilemgr.ERROR

        rslt = self.open_handler(filename)
        if SaveFileMgr.OK == rslt:
            self.filename = filename
            self.clear_changes()
        return rslt

    def _query_unsaved_changes(self):
        # returns: cancel, error, ok
        if not self.unsaved_changes:
            return SaveFileMgr.OK

        dlg = gtk.MessageDialog(None,
                                False,
                                gtk.MESSAGE_QUESTION,
                                gtk.BUTTONS_YES_NO,
                                'Save unsaved changes?')
        dlg.set_transient_for(self.parent_window)
        rslt = dlg.run()
        dlg.destroy()
        if gtk.RESPONSE_NO == rslt:
            return SaveFileMgr.OK
        
        return self.save()

    def quit(self):
        return self._query_unsaved_changes()
