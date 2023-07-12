import os
import sys

def main():
    """
    Main function to facilitate the execution of the command line interface. 
    It handles path settings and initiates the CLI main command execution.
    """

    # Get the directory containing the script
    HERE = os.path.realpath(os.path.dirname(__file__))
    
    # Set an environment variable that points to this script
    os.environ['__E4S_ALC_HOME__'] = os.path.basename(__file__)
    
    # Calculate the absolute path to the parent directory of the project
    E4S_ALC = os.path.join(HERE, '../..')
    
    # Insert E4S_ALC path at the beginning of the Python search path 
    sys.path.insert(0, E4S_ALC)

    # Import the CLI main command to facilitate further actions
    from e4s_alc.cli.__main__ import COMMAND as cli_main_cmd
    
    # Exit and report back the success or failure of the main command
    sys.exit(cli_main_cmd.main())

if __name__ == "__main__":
    main()
