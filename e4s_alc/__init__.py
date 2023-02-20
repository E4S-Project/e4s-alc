import os
import sys

__version__ = "0.0.0"

E4S_ALC_VERSION = __version__

EXIT_FAILURE = -100

EXIT_WARNING = 100

HELP_CONTACT = 'Currently no contact email'

E4S_ALC_URL = 'Currently no website.'

REQUIRED_PYTHON_VERSIONS = [(3, 10)]

# Check for valid versions of python
if not sys.version_info[0:2] in REQUIRED_PYTHON_VERSIONS:
        VERSION = '.'.join([str(x) for x in sys.version_info[0:3]])
        EXPECTED = ' or '.join([(str(x) + '.' + str(y)) for (x, y) in REQUIRED_PYTHON_VERSIONS])
        #TODO implement wrong version of python error

E4S_ALC_HOME = os.path.realpath(os.path.abspath(os.environ.get('__E4S_ALC_HOME__', os.path.join(os.path.dirname(__file__), '..', '..'))))

E4S_ALC_SCRIPT = os.environ.get('__E4S_ALC_SCRIPT__', sys.argv[0] or 'e4s-alc')

USER_PREFIX = os.path.realpath(os.path.abspath(os.environ.get('__E4S_ALC_USER_PREFIX__',
                                                              os.path.join(os.path.expanduser('~'),
                                                                           '.local', 'e4s-alc'))))

def version_banner(): # type: () -> str
    import platform
    import socket
    from datetime import datetime
    import e4s_alc.logger
    fmt = ("E4S-ALC [ %(url)s ]\n"
           "\n"
           "Prefix         : %(prefix)s\n"
           "Version        : %(version)s\n"
           "Timestamp      : %(timestamp)s\n"
           "Hostname       : %(hostname)s\n"
           "Platform       : %(platform)s\n"
           "Working Dir.   : %(cwd)s\n"
           "Terminal Size  : %(termsize)s\n"
           "Frozen         : %(frozen)s\n"
           "Python         : %(python)s\n"
           "Python Version : %(pyversion)s\n"
           "Python Impl.   : %(pyimpl)s\n"
           "PYTHONPATH     : %(pythonpath)s\n")
    data = {"url": E4S_ALC_URL,
            "prefix": E4S_ALC_HOME,
            "version": E4S_ALC_VERSION,
            "timestamp": str(datetime.now()),
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "cwd": os.getcwd(),
            "termsize": 'x'.join([str(dim) for dim in e4s_alc.logger.TERM_SIZE]),
            "frozen": getattr(sys, 'frozen', False),
            "python": sys.executable,
            "pyversion": platform.python_version(),
            "pyimpl": platform.python_implementation(),
            "pythonpath": os.pathsep.join(sys.path)}
    return fmt % data
