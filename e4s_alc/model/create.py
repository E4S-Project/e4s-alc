import os
import sys
import shutil
import logging
from e4s_alc.model import Model
from e4s_alc.conf import get_modules_conf

logger = logging.getLogger('core')

class CreateModel(Model):
    def __init__(self, arg_namespace):
        logger.info("Initializing CreateModel")
        super().__init__(module_name=self.__class__.__name__, arg_namespace=arg_namespace)

    def debug_line(self, line):
        line = logger_line = line.replace('\n', '').replace('\t', '').replace('\\', '')
        logger.debug(f"Adding line: {logger_line}")

    # Instruction adding
    def add_line(self, line, indent=True):
        self.debug_line(line)
        if indent:
            self.instructions.append(f'\t{line}')
        else:
            self.instructions.append(line)

    def add_line_break(self):
        logger.debug("Adding line break")
        self.instructions.append('\n')

    # Base group
    def add_base_image(self):
        logger.debug("Adding base image")
        self.add_line(f'FROM {self.image_registry}{self.base_image} AS base-stage\n\n', indent=False)

    def add_local_files(self):
        if self.local_files:
            logger.debug("Adding local files")
            self.add_line('# Add files from host to container\n')
            for file in self.local_files:
                format_file_spaces = ' '.join(file.split())
                src_file, dest_file = format_file_spaces.split(' ')
                self.add_line(f'ADD {src_file} {dest_file}\n')
            self.add_line_break()

    def add_env_variables(self):
        if self.env_vars:
            logger.debug("Adding environment variables")
            self.add_line('# Set up the environment\n')
            self.env_vars.extend(['DEBIAN_FRONTEND=noninteractive', 'PATH=/spack/bin:$PATH'])
            for env_var in self.env_vars:
                self.add_line(f'ENV {env_var}\n')
            self.add_line_break()

    def add_initial_commands(self):
        if self.initial_commands:
            logger.debug("Adding initial commands")
            self.add_line('# Run commands after pulling the image\n')
            for command in self.initial_commands:
                self.add_line(f'RUN {command}\n')
            self.add_line_break()

    def add_post_base_stage_commands(self):
        if self.post_base_stage_commands:
            logger.debug("Adding post base stage commands")
            self.add_line('# Run commands at the end of the base stage\n')
            for command in self.post_base_stage_commands:
                self.add_line(f'RUN {command}\n')
            self.add_line_break()

    # System group
    def add_certificates(self):
        logger.debug("Adding certificates")
        cert_locations = self.controller.get_certificate_locations(self.certificates)
        if cert_locations:
            self.add_line('# Add certificates\n')
            for cert, new_cert in cert_locations:
                self.add_line(f'ADD {cert} {new_cert}\n')
            update_command = self.controller.get_update_certificate_command()
            self.add_line(f'RUN {update_command}\n\n')

    def add_os_package_commands(self):
        logger.debug("Adding os package commands")
        os_package_commands = self.controller.get_os_package_commands(self.os_packages)
        if os_package_commands:
            self.add_line('# Install OS packages\n')
            for command in os_package_commands:
                self.add_line(f'RUN {command}\n')
            self.add_line_break()

    def add_pre_system_stage_commands(self):
        if self.pre_system_stage_commands:
            logger.debug("Adding pre system stage commands")
            self.add_line('# Run commands at the beginning of the system stage\n')
            for command in self.pre_system_stage_commands:
                self.add_line(f'RUN {command}\n')
            self.add_line_break()

    def add_post_system_stage_commands(self):
        if self.post_system_stage_commands:
            logger.debug("Adding post system stage commands")
            self.add_line('# Run commands at the end of the system stage\n')
            for command in self.post_system_stage_commands:
                self.add_line(f'RUN {command}\n')
            self.add_line_break()

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

        self.add_line(f'# Install Spack version {self.spack_version}\n')
        for command in spack_install_commands:
            self.add_line(f'RUN {command}\n')
        self.add_line_break()

    def add_spack_mirrors(self):
        if self.spack_mirrors:
            logger.debug("Adding spack mirrors")
            self.add_line('# Add Spack mirrors\n')
            for mirror in self.spack_mirrors:
                self.add_line(f'RUN spack mirror add {mirror} {mirror}\n')
            self.add_line('RUN spack buildcache keys --install --trust\n')
            self.add_line_break()

    def copy_conf_file(self):
        logger.debug("Copying conf file")
        file_path = get_modules_conf()
        conf_dir_path = os.path.join(os.getcwd(), 'conf')

        if not os.path.exists(conf_dir_path):
            os.makedirs(conf_dir_path)

        file_name = os.path.basename(file_path)
        dest_path = os.path.join(conf_dir_path, file_name)
        shutil.copy(file_path, dest_path)

    def add_setup_env(self):
        logger.debug("Adding setup env")

        self.add_line('# Setup spack and modules environment\n')
        for command in self.controller.get_env_setup_commands():
            self.add_line(f'RUN {command}\n')
        self.add_line_break()

        self.add_line('# Add module yaml conf file\n')
        self.copy_conf_file()
        self.add_line(f'ADD conf/modules.yaml /spack/etc/spack/modules.yaml\n')
        self.add_line_break()


    def add_post_spack_install_commands(self):
        if self.post_spack_install_commands:
            logger.debug("Adding post spack install commands")
            self.add_line('# Run commands after installing Spack\n')
            for command in self.post_spack_install_commands:
                self.add_line(f'RUN {command}\n')
            self.add_line_break()


    def add_spack_env_install(self):
        logger.debug("Adding spack env install commands")
        self.add_line('# Add Spack env file\n')
        self.add_line(f'ADD {self.spack_env_file} /spack.yaml\n')
        self.add_line('RUN spack --env . install\n')
        self.add_line_break()

    def add_spack_compiler(self):
        if self.spack_compiler:
            logger.debug("Adding spack compiler")
            self.add_line('# Installing Spack compiler\n')

            compiler, package, version = None, None, None
            
            # Check if self.spack_compiler is 'llvm'
            if self.spack_compiler == 'llvm':
                compiler = 'clang'
                self.spack_compiler += '+flang'
            else:
                # Splitting package and version if '@' is present
                if '@' in self.spack_compiler:
                    package, version = self.spack_compiler.split('@')

                # Set 'compiler' based on 'package' if it's not None, otherwise set to self.spack_compiler
                compiler = 'clang' if package == 'llvm' else package or self.spack_compiler

                if package == 'llvm':
                    version_suffix = f'@{version}' if version else ''
                    self.spack_compiler += f'{version_suffix}+flang'

            
            signature_check = ''
            if not self.spack_check_signature:
                signature_check = '--no-check-signature '

            spack_compiler_commands = [
                'spack compiler find',
                f'spack install {signature_check}{self.spack_compiler}',
                'spack module tcl refresh -y 1> /dev/null',
                f'. /etc/profile.d/setup-env.sh && spack load {self.spack_compiler} && spack compiler find',
                'spack compiler rm "gcc@"$(/usr/bin/gcc -dumpversion)',
                f'spack config add "packages:all:compiler:[{compiler}]"'
            ]

            for command in spack_compiler_commands:
                self.add_line(f'RUN {command}\n')
            self.add_line_break()

    def add_spack_packages(self):
        if self.spack_packages:
            logger.debug("Adding spack packages")

            signature_check = ''
            if not self.spack_check_signature:
                signature_check = '--no-check-signature '

            self.add_line('# Install Spack packages\n')
            for package in self.spack_packages:
                self.add_line(f'RUN spack install {signature_check}{package}\n')
            self.add_line_break()

    def add_pre_spack_stage_commands(self):
        if self.pre_spack_stage_commands:
            logger.debug("Adding pre spack stage commands")
            self.add_line('# Run commands at the beginning of the Spack stage\n')
            for command in self.pre_spack_stage_commands:
                self.add_line(f'RUN {command}\n')
            self.add_line_break()

    def add_post_spack_stage_commands(self):
        if self.post_spack_stage_commands:
            logger.debug("Adding post spack stage commands")
            self.add_line('# Run commands at the end of the Spack stage\n')
            for command in self.post_spack_stage_commands:
                self.add_line(f'RUN {command}\n')
            self.add_line_break()

    def add_entrypoint(self):
        self.add_line('# Entrypoint of the image\n')
        self.add_line('ENTRYPOINT ["/bin/bash"]\n')

    def export_to_makefile(self):
        logger.info("Exporting to makefile")
        with open('Dockerfile', 'w') as f:
            for instruction in self.instructions:
                f.write(instruction)

    # Add stages
    def create_base_stage(self):
        logger.info("Creating base stage")
        self.add_line('# Base Stage\n', indent=False)
        self.add_base_image()
        self.add_initial_commands()
        self.add_local_files()
        self.add_env_variables()
        self.add_post_base_stage_commands()

    def create_system_stage(self):
        logger.info("Creating system stage")
        self.add_line('# System Stage\n', indent=False)
        self.add_line(f'FROM base-stage AS system-stage\n\n', indent=False)
        self.add_pre_system_stage_commands()
        self.add_os_package_commands()
        self.add_certificates()
        self.add_post_system_stage_commands()

    def create_spack_stage(self):
        logger.info("Creating spack stage")
        self.add_line('# Spack Stage\n', indent=False)
        self.add_line(f'FROM system-stage AS spack-stage\n\n', indent=False)
        self.add_pre_spack_stage_commands()
        self.add_spack()
        self.add_spack_mirrors()
        self.add_setup_env()
        self.add_post_spack_install_commands()
        self.add_spack_compiler()
        if self.spack_env_file:
            self.add_spack_env_install()
        else:
            self.add_spack_packages()

        self.add_line('# Update compiler list\n')
        self.add_line('RUN spack compiler find\n')
        self.add_line_break()
        self.add_post_spack_stage_commands()

    def create_finalize_stage(self):
        logger.info("Creating finalize stage")
        self.add_line('# Finalize Stage\n', indent=False)
        if self.spack_install:
            self.add_line(f'FROM spack-stage AS finalize-stage\n\n', indent=False)
        else:
            self.add_line(f'FROM system-stage AS finalize-stage\n\n', indent=False)

        self.add_entrypoint()
        self.export_to_makefile()

    def create(self):
        logger.info("Creating stages")
        self.create_base_stage()
        self.create_system_stage()
        if self.spack_install:
            self.create_spack_stage()
        self.create_finalize_stage()
