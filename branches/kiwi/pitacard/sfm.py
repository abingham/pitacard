class SaveFileMgr:
    OK     = 0
    ERROR  = 1
    CANCEL = 2

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
        self.formats.push_back((name, suffix, id))

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
        pass

    def open(self):
        '''
        returns: cancel, error, ok
        '''
        pass

    def _save(self, filename):
        if not self.save_handler:
            error.error('no save handler set...yell at the developers!')
            return SaveFileMgr.ERROR

        if not os.access(filename, os.W_OK):
            error.error('%s is not writable' % filename)
            return SaveFileMgr.ERROR

        rslt = self.save_handler(filename)
        if rslt == SaveFileMgr.OK:
            self.filename = filename
            self.unsaved_changes = False
        return rslt

    def _query_unsaved_changes(self):
        # returns: cancel, error, ok
        pass
