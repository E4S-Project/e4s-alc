import sys
import logging
import inspect
import functools

def get_subpath(path):
    identifier = 'e4s_alc'
    if identifier in path:
        return path[path.index(identifier):]
    else:
        return ''

def log_info(message):
    logger = logging.getLogger('core')
    logger.info(message)

def log_error(message):
    logger = logging.getLogger('core')
    logger.error(message)

def log_function_call(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger('core')
        subpath = get_subpath(inspect.getfile(f))
        logger.debug(f"{subpath}: Calling: {f.__qualname__}")
        return f(*args, **kwargs)
    return wrapper

class Logger:
    def __init__(self, log_name, log_file, verbose=False):
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(logging.DEBUG)  

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
   
        # File Handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)
        
        # Stream Handler for stdout
        if verbose:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            console_handler.setLevel(logging.DEBUG)
            self.logger.addHandler(console_handler)

    def log(self, msg, level):
        if level.lower() == 'info':
            self.logger.info(msg)
        elif level.lower() == 'error':
            self.logger.error(msg, exc_info=True)
        elif level.lower() == 'debug':
            self.logger.debug(msg)
        elif level.lower() == 'warning':
            self.logger.warning(msg)
        else:
            self.logger.critical(msg)

    def info(self, msg):
        self.log(msg, 'info')

    def error(self, msg):
        self.log(msg, 'error')

    def debug(self, msg):
        self.log(msg, 'debug')

    def warning(self, msg):
        self.log(msg, 'warning')

    def critical(self, msg):
        self.log(msg, 'critical')
