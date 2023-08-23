import os
import subprocess
from e4s_alc.controller import Controller, Compiler
from e4s_alc.util import log_function_call, log_info, log_error, BackendMissingError, YAMLNotFoundError

class Model():

    _spack_version_cache = None

    @log_function_call
    def __init__(self, module_name, arg_namespace):
        self.module_name = module_name
        self.matrix = None 
        self.controller = None
        self.instructions = []

        # Base group
        self.backend = None
        self.base_image = None
        self.image_registry = None
        self.full_image_path = None
        self.local_files = None
        self.env_vars = None
        self.initial_commands = None
        self.post_base_stage_commands = None

        # System group
        self.certificates = None
        self.os_packages = None
        self.remote_files = None
        self.git_repos = None
        self.pre_system_stage_commands = None
        self.post_system_stage_commands = None

        # Spack group
        self.spack_install = None
        self.spack_version = None
        self.spack_mirrors = None
        self.spack_check_signature = None
        self.modules_yaml_file = None
        self.spack_compiler = None
        self.spack_yaml_file = None
        self.spack_packages = None
        self.pre_spack_stage_commands = None
        self.post_spack_install_commands = None
        self.post_spack_stage_commands = None

        # Finalize group
        self.registry_image_matrix = None
        self.spack_version_matrix = None
        self.spack_compiler_matrix = None

        self.read_arguments(arg_namespace)
        self.controller = Controller(self.backend, self.full_image_path)

    @log_function_call
    def read_arguments(self, args):

        # Base group
        self.backend = args.get('backend', None)
        if not self.backend:
            self.backend = self.discover_backend()

        self.base_image = args.get('image', None)
        self.image_registry = self.none_to_blank(args.get('registry', ''))
        if self.image_registry:
            if not self.image_registry.endswith('/'):
                self.image_registry += '/'

        self.full_image_path = self.image_registry + self.base_image
        self.local_files = self.remove_nones(args.get('add-files', []))
        self.env_vars = self.remove_nones(args.get('env-variables', []))
        self.initial_commands = self.remove_nones(args.get('initial-commands', []))
        self.post_base_stage_commands = self.remove_nones(args.get('post-base-stage-commands', []))

        # System group
        self.os_packages = self.remove_nones(args.get('os-packages', []))
        self.certificates = self.remove_nones(args.get('certificates', []))
        self.remote_files = self.remove_nones(args.get('add-remote-files', []))
        self.git_repos = self.remove_nones(args.get('add-repos', []))
        self.pre_system_stage_commands = self.remove_nones(args.get('pre-system-stage-commands', []))
        self.post_system_stage_commands = self.remove_nones(args.get('post-system-stage-commands', []))

        # Spack group
        self.spack_install = self.string_to_bool(args.get('spack', True))
        self.spack_version = args.get('spack-version', None)
        if self.spack_version == 'latest' or self.spack_version == None:
            self.spack_version = self.discover_latest_spack_version()

        self.spack_mirrors = self.remove_nones(args.get('spack-mirrors', []))
        self.spack_check_signature = self.string_to_bool(args.get('spack-check-signature', True))
        self.modules_yaml_file = args.get('modules-yaml-file', None)
        self.spack_compiler = args.get('spack-compiler', None)
        if self.spack_compiler:
            self.spack_compiler = Compiler(self.spack_compiler) 

        self.spack_yaml_file = args.get('spack-yaml-file', None)
        self.spack_packages = self.remove_nones(args.get('spack-packages', []))
        self.pre_spack_stage_commands = self.remove_nones(args.get('pre-spack-stage-commands', []))
        self.post_spack_install_commands = self.remove_nones(args.get('post-spack-install-commands', []))
        self.post_spack_stage_commands = self.remove_nones(args.get('post-spack-stage-commands', []))

        # Finalize group
        self.matrix = args.get('matrix', False)
        if self.matrix:
            self.registry_image_matrix = args.get('registry-image-matrix', [])
            self.spack_version_matrix = args.get('spack-version-matrix', [])
            self.spack_compiler_matrix = args.get('spack-compiler-matrix', [])

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

    @log_function_call
    def discover_backend(self):        
        # Capture exit status of container version
        # The exit status is flipped to return a True/False
        log_info("Checking for podman...")
        podman_check = not os.system('podman -v &> /dev/null')
        
        if podman_check:
            log_info("Podman found.")
            return 'podman'
        
        log_info("Checking for docker...")
        docker_check = not os.system('docker -v &> /dev/null')
        
        if docker_check:
            log_info("Docker found.")
            return 'docker'
        
        log_error("No backend (podman or docker) found.")
        raise BackendMissingError

    @log_function_call
    def discover_latest_spack_version(self):
        if Model._spack_version_cache:
            log_info("Found cached spack version: " + Model._spack_version_cache)
            return Model._spack_version_cache

        # create the curl, grep, and sed commands as strings
        curl_command = 'curl --silent "https://api.github.com/repos/spack/spack/releases/latest"'
        grep_command = "grep '\"tag_name\":'"
        sed_command = "sed -E 's/.*\"([^\"]+)\".*/\\1/'"

        # add the commands together
        full_command = curl_command + " | " + grep_command + " | " + sed_command
        log_info("Final command to execute: " + full_command)

        output = subprocess.check_output(full_command, shell=True)
        version_number = output.decode('utf-8').strip().replace('v', '')

        if not version_number:
            log_info('Failed to discover latest Spack version. Defaulting to Spack v0.20.1')
            version_number = '0.20.1'
        else:
            log_info('Discovered latest spack version: ' + version_number)

        Model._spack_version_cache = version_number
        return version_number
