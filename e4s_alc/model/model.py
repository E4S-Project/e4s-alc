import os
import yaml
import subprocess
import logging
from e4s_alc.util import BackendMissingError, YAMLNotFoundError

logger = logging.getLogger('core')

class Model():
    def __init__(self, module_name, arg_namespace):
        logger.info("Initializing Model")
        self.module_name = module_name
        self.controller = None
        self.instructions = []

        # Definition file specific attributes
        self.header = []
        self.environment = []
        self.files = []
        self.post = []
        self.startscript = []

        # Base group
        self.backend = None
        self.bootstrap = None
        self.base_image = None
        self.image_registry = None
        self.local_files = None
        self.env_vars = None
        self.initial_commands = None
        self.post_base_stage_commands = None

        # System group
        self.certificates = None
        self.os_packages = None
        self.pre_system_stage_commands = None
        self.post_system_stage_commands = None

        # Spack group
        self.spack_install = None
        self.spack_version = None
        self.spack_mirrors = None
        self.spack_check_signature = None
        self.modules_env_file = None
        self.spack_compiler = None
        self.spack_env_file = None
        self.spack_packages = None
        self.pre_spack_stage_commands = None
        self.post_spack_install_commands = None
        self.post_spack_stage_commands = None

        self.read_arguments(arg_namespace)

    def read_arguments_from_file(self, file_path):
        logger.info("Reading arguments from file")
        abs_file_path = os.path.abspath(file_path)

        if not os.path.isfile(abs_file_path):
            raise YAMLNotFoundError(abs_file_path)

        with open(abs_file_path, 'r') as file:
            if file_path.endswith('.yaml'):
                data = yaml.safe_load(file)
            else:
                print('Invalid file format. Please provide .yaml file format. Run `e4s-alc template` to generate a template .yaml file.')
                exit(1)
        return data

    def read_arguments(self, arg_namespace):
        logger.info("Reading arguments")
        args = vars(arg_namespace)

        # File group
        if args['file']:
            args = self.read_arguments_from_file(args['file']) 

        # Base group
        self.backend = args.get('backend', None)
        if not self.backend:
            self.backend = self.discover_backend()
        self.base_image = args.get('image', None) or self.raise_argument_error('image')
        self.image_registry = self.none_to_blank(args.get('registry', ''))
        if self.image_registry:
            if not self.image_registry.endswith('/'):
                self.image_registry += '/'

        self.local_files = self.remove_nones(args.get('add-files', []))
        self.env_vars = self.remove_nones(args.get('env-variables', []))
        self.initial_commands = self.remove_nones(args.get('initial-commands', []))
        self.post_base_stage_commands = self.remove_nones(args.get('post-base-stage-commands', []))

        # System group
        self.certificates = self.remove_nones(args.get('certificates', []))
        self.os_packages = self.remove_nones(args.get('os-packages', []))
        self.pre_system_stage_commands = self.remove_nones(args.get('pre-system-stage-commands', []))
        self.post_system_stage_commands = self.remove_nones(args.get('post-system-stage-commands', []))

        # Spack group
        self.spack_install = self.string_to_bool(args.get('spack', True))
        self.spack_version = args.get('spack-version', self.discover_latest_spack_version())
        if self.spack_version == 'latest':
            self.spack_version = self.discover_latest_spack_version()

        self.spack_mirrors = self.remove_nones(args.get('spack-mirrors', []))
        self.spack_check_signature = self.string_to_bool(args.get('spack-check-signature', True))

        self.modules_env_file = args.get('modules-env-file', None)
        self.spack_compiler = args.get('spack-compiler', None)
        self.spack_env_file = args.get('spack-env-file', None)
        self.spack_packages = self.remove_nones(args.get('spack-packages', []))
        self.pre_spack_stage_commands = self.remove_nones(args.get('pre-spack-stage-commands', []))
        self.post_spack_install_commands = self.remove_nones(args.get('post-spack-install-commands', []))
        self.post_spack_stage_commands = self.remove_nones(args.get('post-spack-stage-commands', []))

    def remove_nones(self, l):
        return [s for s in l if s != None]

    def string_to_bool(self, s):
        if isinstance(s, str):
            return s.lower() == 'true'
        if isinstance(s, bool):
            return s

    def none_to_blank(self, n):
        if n == None: 
            return ''
        else:
            return n

    def discover_backend(self):        
        logger.info("Discovering backend")
        # Capture exit status of container version
        # The exit status is flipped to return a True/False
        podman_check = not os.system('podman -v &> /dev/null')
        docker_check = not os.system('docker -v &> /dev/null')

        if podman_check:
            return 'podman' 

        if docker_check:
            return 'docker'

        raise BackendMissingError        

    def discover_latest_spack_version(self):
        logger.info("Discovering latest spack version")

        # create the curl, grep, and sed commands as strings
        curl_command = 'curl --silent "https://api.github.com/repos/spack/spack/releases/latest"'
        grep_command = "grep '\"tag_name\":'"
        sed_command = "sed -E 's/.*\"([^\"]+)\".*/\\1/'"

        # add the commands together
        full_command = curl_command + " | " + grep_command + " | " + sed_command
        
        output = subprocess.check_output(full_command, shell=True)
        version_number = output.decode('utf-8').strip().replace('v', '')
        return version_number 

    def raise_argument_error(self, argument):
        print(f'ERROR: add raise here {argument}')
        exit(1)
