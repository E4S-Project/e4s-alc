import os
import sys
import shutil
import logging
from e4s_alc.model import Model
from e4s_alc.controller.controller import Controller
from e4s_alc.util import log_function_call

logger = logging.getLogger('core')

class CreateDefinitionfileModel(Model):
    def __init__(self, arg_namespace):
        logger.info("Initializing CreateModel")
        super().__init__(module_name=self.__class__.__name__, arg_namespace=arg_namespace)
        self.controller = Controller(self.backend, self.image_registry + self.base_image, self.repull)

    def debug_line(self, line):
        line = logger_line = line.replace('\n', '').replace('\t', '').replace('\\', '')
        logger.debug(f"Adding line: {logger_line}")

    # Instruction adding
    def add_line(self, line, section, indent=True):
        self.debug_line(line)
        if indent:
            getattr(self, section).append(f'\t{line}')
        else:
            getattr(self, section).append(line)

    def add_line_break(self, section):
        logger.debug("Adding line break")
        getattr(self, section).append('\n')

    # Base group
    def add_base_image(self):
        logger.debug("Adding base image")
        self.add_line(f'From: {self.image_registry}{self.base_image}\n\n', "header", indent=False)

    def add_local_files(self):
        if self.local_files:
            logger.debug("Adding local files")
            for file in self.local_files:
                format_file_spaces = ' '.join(file.split())
                src_file, dest_file = format_file_spaces.split(' ')
                self.add_line(f'{src_file} {dest_file}\n', "files")

    def add_env_variables(self):
        self.env_vars.extend(['DEBIAN_FRONTEND=noninteractive', 'PATH=/spack/bin:$PATH'])
        logger.debug("Adding environment variables")
        for env_var in self.env_vars:
            if "export" in env_var:
                self.add_line(f'{env_var}\n', "environment")
            else:
                self.add_line(f'export {env_var}\n', "environment")
        self.add_line_break("environment")

    def add_initial_commands(self):
        if self.initial_commands:
            logger.debug("Adding initial commands")
            for command in self.initial_commands:
                self.add_line(f'{command}\n', "post")
            self.add_line_break("post")

    def add_post_base_stage_commands(self):
        if self.post_base_stage_commands:
            logger.debug("Adding post base stage commands")
            for command in self.post_base_stage_commands:
                self.add_line(f'{command}\n', "post")
            self.add_line_break("post")

    def add_pre_system_stage_commands(self):
        if self.pre_system_stage_commands:
            logger.debug("Adding pre system stage commands")
            for command in self.pre_system_stage_commands:
                self.add_line(f'{command}\n', "post")
            self.add_line_break("post")

    def add_certificates(self):
        logger.debug("Adding certificates")
        cert_locations = self.controller.get_certificate_locations(self.certificates)
        if cert_locations:
            self.add_line('# Add certificates\n', "files")
            for cert, new_cert in cert_locations:
                self.add_line(f'{cert} {new_cert}\n', "files")
            self.add_line_break("files")
            update_command = self.controller.get_update_certificate_command()
            self.add_line(f'{update_command}\n\n', "post")

    def add_post_system_stage_commands(self):
        if self.post_system_stage_commands:
            logger.debug("Adding post system stage commands")
            for command in self.post_system_stage_commands:
                self.add_line(f'{command}\n', "post")
            self.add_line_break("post")

    def add_os_package_commands(self):
        logger.debug("Adding os package commands")
        os_package_commands = self.controller.get_os_package_commands(self.os_packages)
        if os_package_commands:
            self.add_line('# Install OS packages\n', "post")
            for command in os_package_commands:
                self.add_line(f'{command}\n', "post")
            self.add_line_break("post")

    # Spack group
    def add_spack(self):
        logger.debug("Adding spack")
        spack_url = f'https://github.com/spack/spack/releases/download/v{self.spack_version}/spack-{self.spack_version}.tar.gz'

        spack_install_commands = [
            f'curl -L {spack_url} -o /spack.tar.gz',
            'gzip -d /spack.tar.gz && tar -xf /spack.tar && rm /spack.tar',
            f'mv /spack-{self.spack_version} /spack && . /spack/share/spack/setup-env.sh',
            'echo export PATH=/spack/bin:$PATH >> ~/.bashrc'
        ]

        self.add_line(f'# Install Spack version {self.spack_version}\n', "post")
        for command in spack_install_commands:
            self.add_line(f'{command}\n', "post")
        self.add_line_break("post")

    def add_spack_mirrors(self):
        if self.spack_mirrors:
            logger.debug("Adding spack mirrors")
            self.add_line('# Add Spack mirrors\n', "post")
            for mirror in self.spack_mirrors:
                self.add_line(f'spack mirror add {mirror} {mirror}\n', "post")
            self.add_line('spack buildcache keys --install --trust\n', "post")
            self.add_line_break("post")

    def add_setup_env(self):
        self.add_line('# Setup spack and modules environment\n', "post")
        command = ' && \\\n\t    '.join(self.controller.get_env_setup_commands())
        self.add_line(f'{command}\n', "post")
        self.add_line_break("post")

    def add_modules_file(self):
        if self.modules_yaml_file:
            self.add_line('# Add modules.yaml file\n', "files")
            self.add_line(f'{self.modules_yaml_file} /spack/etc/spack/modules.yaml\n', "files")
            self.add_line_break("files")
        else:
            self.add_line('# Add modules.yaml file\n', "post")
            self.add_line(f'curl https://www.nic.uoregon.edu/~cfd/e4s-alc/modules.yaml -o /spack/etc/spack/modules.yaml\n', "post")
            self.add_line_break("post")

    def add_post_spack_install_commands(self):
        if self.post_spack_install_commands:
            logger.debug("Adding post spack install commands")
            self.add_line('# Run commands after installing Spack\n', "post")
            for command in self.post_spack_install_commands:
                self.add_line(f'{command}\n', "post")
            self.add_line_break("post")

    def add_spack_yaml_install(self):
        signature_check = ''
        if not self.spack_check_signature:
            signature_check = '--no-check-signature'

        logger.debug("Adding spack env install commands")
        self.add_line('# Add Spack env file\n', "files")
        self.add_line(f'{self.spack_yaml_file} /spack.yaml\n', "files")
        self.add_line(f'spack --env / install {signature_check}\n', "post")
        self.add_line_break("files")
        self.add_line_break("post")

    @log_function_call
    def add_spack_compiler(self):
        if self.spack_compiler:
            self.add_line('# Installing Spack compiler\n', "post")
            spack_compiler_commands = self.spack_compiler.get_spack_compiler_commands(self.spack_check_signature)
            for command in spack_compiler_commands:
                self.add_line(f'{command}\n', "post")
            self.add_line_break("post")

    def add_spack_packages(self):
        if self.spack_packages:
            logger.debug("Adding spack packages")

            signature_check = ''
            if not self.spack_check_signature:
                signature_check = '--no-check-signature '

            self.add_line('# Install Spack packages\n', "post")
            for package in self.spack_packages:
                self.add_line(f'spack install {signature_check}{package}\n', "post")
            self.add_line_break("post")

    def add_pre_spack_stage_commands(self):
        if self.pre_spack_stage_commands:
            logger.debug("Adding pre spack stage commands")
            self.add_line('# Run commands at the beginning of the Spack stage\n', "post")
            for command in self.pre_spack_stage_commands:
                self.add_line(f'{command}\n', "post")
            self.add_line_break("post")

    def add_post_spack_stage_commands(self):
        if self.post_spack_stage_commands:
            logger.debug("Adding post spack stage commands")
            self.add_line('# Run commands at the end of the Spack stage\n', "post")
            for command in self.post_spack_stage_commands:
                self.add_line(f'{command}\n', "post")
            self.add_line_break("post")

    def add_bootstrap(self):
        if not self.bootstrap:
            self.bootstrap = "docker"
        self.add_line(f"Bootstrap: {self.bootstrap}\n", "header", indent=False)

    def export_to_makefile(self):
        logger.info("Exporting to makefile")
        output_file = self.name if self.name else 'singularity.def'
        with open(output_file, 'w') as f:
            for line in self.header:
                f.write(line)
            for line in self.environment:
                f.write(line)
            for line in self.files:
                f.write(line)
            for line in self.post:
                f.write(line)
            for line in self.startscript:
                f.write(line)
            for line in self.runscript:
                f.write(line)

    # Add stages
    def create_header(self):
        logger.info("Creating header")
        self.add_bootstrap()
        self.add_base_image()

    def create_environment(self):
        self.add_line('%environment\n', "environment", indent=False)
        self.add_env_variables()

    def create_files(self):
        self.add_line('%files\n', "files", indent=False)
        self.add_local_files()

    def create_post(self):
        self.add_line('%post\n', "post", indent=False)
        self.add_line('export DEBIAN_FRONTEND=noninteractive\n', "post")
        self.add_line_break("post")
        self.add_initial_commands()
        self.add_post_base_stage_commands()
        self.add_pre_system_stage_commands()
        self.add_certificates()
        self.add_os_package_commands()
        self.add_post_system_stage_commands()
        if self.spack_install:
            self.add_pre_spack_stage_commands()
            self.add_spack()
            self.add_spack_mirrors()
            self.add_post_spack_install_commands()

            self.add_setup_env()
            self.add_modules_file()

            self.add_spack_compiler()
            if self.spack_yaml_file:
                self.add_spack_yaml_install()
            else:
                self.add_spack_packages()
            self.add_line('spack compiler find\n', "post")
            self.add_post_spack_stage_commands()
            self.add_line_break("post")

    def convert_to_bash_script(self, command, section):
        logger.debug("Converting command to bash script")
        self.add_line(f'#!{command[1]}\n', section)
        self.add_line(f'{command[5]}\n', section)

    def create_startscript(self):
        logger.debug("Adding startscript")
        self.add_line('%startscript\n', "startscript", indent=False)
        command = self.controller.get_entrypoint_command()
        self.convert_to_bash_script(command.split('"'), "startscript")
        self.add_line_break("startscript")

    def create_runscript(self):
        logger.debug("Adding runscript")
        self.add_line('%runscript\n', "runscript", indent=False)
        command = self.controller.get_entrypoint_command()
        self.convert_to_bash_script(command.split('"'), "runscript")

    def create_sections(self):
        self.create_environment()
        self.create_files()
        self.create_post()
        self.create_startscript()
        self.create_runscript()

    def create(self):
        logger.info("Creating stages")
        self.create_header()
        self.create_sections()
        self.export_to_makefile()
