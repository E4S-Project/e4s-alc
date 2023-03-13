def main():
    import os
    import sys

    HERE = os.path.realpath(os.path.dirname(__file__))
    os.environ['__E4S_ALC_HOME__'] = os.path.join(HERE, '../../..')
    os.environ['__E4S_ALC_HOME__'] = os.path.basename(__file__)
    E4S_ALC = os.path.join(HERE, '../../..')
    sys.path.insert(0, E4S_ALC)

    from e4s_alc.cli.__main__ import COMMAND as cli_main_cmd
    sys.exit(cli_main_cmd.main(sys.argv[1:]))
