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
