import os
import sys
import shutil
import logging
from e4s_alc.model import Model
from e4s_alc.conf import get_modules_conf
from e4s_alc.util import log_function_call

logger = logging.getLogger('core')

class CreateModel(Model):
    @log_function_call
    def __init__(self, arg_namespace):
        super().__init__(module_name=self.__class__.__name__, arg_namespace=arg_namespace)

    def log_line(self, line):
        logger_line = line.replace('\n', '').replace('\t', '').replace('\\', '')
        logger.info(f"Instructions - Adding line: {logger_line}")

    # Instruction adding
    def add_line(self, line, indent=True):
        if indent:
            self.instructions.append(f'\t{line}')
        else:
            self.instructions.append(line)

    def add_line_break(self):
        self.instructions.append('\n')

    # Base group
    @log_function_call
    def add_base_image(self):
        self.add_line(f'FROM {self.full_image_path} AS base-stage\n\n', indent=False)

    @log_function_call
    def add_local_files(self):
        if self.local_files:
            self.add_line('# Add files from host to container\n')
            for file in self.local_files:
                format_file_spaces = ' '.join(file.split())
                src_file, dest_file = format_file_spaces.split(' ')
                self.add_line(f'ADD {src_file} {dest_file}\n')
            self.add_line_break()

    @log_function_call
    def add_env_variables(self):
        self.env_vars.extend(['DEBIAN_FRONTEND=noninteractive', 'PATH=/spack/bin:$PATH'])
        self.add_line('# Set up the environment\n')
        for env_var in self.env_vars:
            self.add_line(f'ENV {env_var}\n')
        self.add_line_break()

    @log_function_call
    def add_initial_commands(self):
        if self.initial_commands:
            self.add_line('# Run commands after pulling the image\n')
            for command in self.initial_commands:
                self.add_line(f'RUN {command}\n')
            self.add_line_break()

    @log_function_call
    def add_post_base_stage_commands(self):
        if self.post_base_stage_commands:
            self.add_line('# Run commands at the end of the base stage\n')
            for command in self.post_base_stage_commands:
                self.add_line(f'RUN {command}\n')
            self.add_line_break()

    # System group
    @log_function_call
    def add_os_package_commands(self):
        os_package_commands = self.controller.get_os_package_commands(self.os_packages)
        self.add_line('# Install OS packages\n')
        for command in os_package_commands:
            self.add_line(f'RUN {command}\n')
        self.add_line_break()

    @log_function_call
    def add_certificates(self):
        cert_locations = self.controller.get_certificate_locations(self.certificates)
        if cert_locations:
            self.add_line('# Add certificates\n')
            for cert, new_cert in cert_locations:
                self.add_line(f'ADD {cert} {new_cert}\n')
            update_command = self.controller.get_update_certificate_command()
            self.add_line(f'RUN {update_command}\n\n')

    @log_function_call
    def add_github_repos(self):
        if self.git_repos:
            self.add_line('# Clone GitHub repos\n')
            for repo in self.git_repos:
                self.add_line(f'RUN git clone {repo}\n')
            self.add_line_break()

    @log_function_call
    def add_pre_system_stage_commands(self):
        if self.pre_system_stage_commands:
            self.add_line('# Run commands at the beginning of the system stage\n')
            for command in self.pre_system_stage_commands:
                self.add_line(f'RUN {command}\n')
            self.add_line_break()

    @log_function_call
    def add_post_system_stage_commands(self):
        if self.post_system_stage_commands:
            self.add_line('# Run commands at the end of the system stage\n')
            for command in self.post_system_stage_commands:
                self.add_line(f'RUN {command}\n')
            self.add_line_break()

    # Spack group
    @log_function_call
    def add_spack(self):
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

    @log_function_call
    def add_spack_mirrors(self):
        if self.spack_mirrors:
            self.add_line('# Add Spack mirrors\n')
            for mirror in self.spack_mirrors:
                self.add_line(f'RUN spack mirror add {mirror} {mirror}\n')
            self.add_line('RUN spack buildcache keys --install --trust\n')
            self.add_line_break()

    @log_function_call
    def copy_conf_file(self):
        file_path = get_modules_conf()

        if self.matrix:
            conf_dir_path = os.path.join(os.getcwd(), 'dockerfiles', '.conf')
        else:
            conf_dir_path = os.path.join(os.getcwd(), '.conf')

        if not os.path.exists(conf_dir_path):
            os.makedirs(conf_dir_path)

        file_name = os.path.basename(file_path)
        dest_path = os.path.join(conf_dir_path, file_name)
        shutil.copy(file_path, dest_path)

    @log_function_call
    def add_setup_env(self):
        self.add_line('# Setup spack and modules environment\n')
        for command in self.controller.get_env_setup_commands():
            self.add_line(f'RUN {command}\n')
        self.add_line_break()

    @log_function_call
    def add_modules_file(self):
        self.add_line('# Add modules.yaml file\n')
        if self.modules_yaml_file:
            self.add_line(f'ADD {self.modules_yaml_file} /spack/etc/spack/modules.yaml\n')
        else:
            self.copy_conf_file()
            self.add_line(f'ADD .conf/modules.yaml /spack/etc/spack/modules.yaml\n')
        self.add_line_break()

    @log_function_call
    def add_post_spack_install_commands(self):
        if self.post_spack_install_commands:
            self.add_line('# Run commands after installing Spack\n')
            for command in self.post_spack_install_commands:
                self.add_line(f'RUN {command}\n')
            self.add_line_break()

    @log_function_call
    def add_spack_yaml_install(self):
        signature_check = ''
        if not self.spack_check_signature:
            signature_check = '--no-check-signature'

        self.add_line('# Add Spack env file\n')
        self.add_line(f'ADD {self.spack_yaml_file} /spack.yaml\n')
        self.add_line(f'RUN spack env create main /spack.yaml\n')
        self.add_line(f'RUN spack --env main install {signature_check}\n')
        self.add_line_break()

    @log_function_call
    def add_create_spack_env(self):
        self.add_line('# Create a Spack environment\n')
        self.add_line('RUN spack env create main\n')
        self.add_line_break()

    @log_function_call
    def add_spack_compiler(self):
        if self.spack_compiler:
            self.add_line('# Installing Spack compiler\n')
            spack_compiler_commands = self.spack_compiler.get_spack_compiler_commands(self.spack_check_signature)
            for command in spack_compiler_commands:
                self.add_line(f'RUN {command}\n')
            self.add_line_break()

    @log_function_call
    def add_spack_packages(self):
        if self.spack_packages:
            signature_check = ''
            if not self.spack_check_signature:
                signature_check = '--no-check-signature '

            self.add_line('# Install Spack packages\n')
            env_install = '. /spack/share/spack/setup-env.sh && spack env activate main &&' 
            for package in self.spack_packages:
                self.add_line(f'RUN {env_install} spack install --add {signature_check}{package}\n')
            self.add_line_break()

    @log_function_call
    def add_pre_spack_stage_commands(self):
        if self.pre_spack_stage_commands:
            self.add_line('# Run commands at the beginning of the Spack stage\n')
            for command in self.pre_spack_stage_commands:
                self.add_line(f'RUN {command}\n')
            self.add_line_break()

    @log_function_call
    def add_post_spack_stage_commands(self):
        if self.post_spack_stage_commands:
            self.add_line('# Run commands at the end of the Spack stage\n')
            for command in self.post_spack_stage_commands:
                self.add_line(f'RUN {command}\n')
            self.add_line_break()

    @log_function_call
    def add_entrypoint(self):
        self.add_line('# Entrypoint of the image\n')
        command = self.controller.get_entrypoint_command()
        self.add_line(f'ENTRYPOINT [{command}]\n')

    @log_function_call
    def export_dockerfile_matrix(self):
        directory = './dockerfiles'
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        os_id = self.controller.get_os_id_and_version()
        file_name = f'{directory}/Dockerfile.{os_id}-{self.spack_compiler.compiler}@{self.spack_compiler.version}' 
        with open(file_name, 'w') as f:
            for instruction in self.instructions:
                self.log_line(instruction)
                f.write(instruction)

    @log_function_call
    def export_to_dockerfile(self):
        with open('Dockerfile', 'w') as f:
            for instruction in self.instructions:
                self.log_line(instruction)
                f.write(instruction)

    # Add stages
    @log_function_call
    def create_base_stage(self):
        self.add_line('# Base Stage\n', indent=False)
        self.add_base_image()
        self.add_initial_commands()
        self.add_local_files()
        self.add_env_variables()
        self.add_post_base_stage_commands()

    @log_function_call
    def create_system_stage(self):
        self.add_line('# System Stage\n', indent=False)
        self.add_line(f'FROM base-stage AS system-stage\n\n', indent=False)
        self.add_pre_system_stage_commands()

        # If rockylinux (and others? not ubuntu):
        #   Add certs before packages
        if self.controller.get_os_id() == 'rocky':
            self.add_certificates()
            self.add_os_package_commands()
        else:
            self.add_os_package_commands()
            self.add_certificates()

        self.add_github_repos()
        self.add_post_system_stage_commands()

    @log_function_call
    def create_spack_stage(self):
        self.add_line('# Spack Stage\n', indent=False)
        self.add_line(f'FROM system-stage AS spack-stage\n\n', indent=False)
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
            self.add_create_spack_env()
            self.add_spack_packages()

        # self.add_packages to moduels
        self.add_line('# Update compiler list\n')
        self.add_line('RUN spack compiler find\n')
        self.add_line_break()
        self.add_post_spack_stage_commands()

    @log_function_call
    def create_finalize_stage(self):
        self.add_line('# Finalize Stage\n', indent=False)

        if self.spack_install:
            self.add_line(f'FROM spack-stage AS finalize-stage\n\n', indent=False)
        else:
            self.add_line(f'FROM system-stage AS finalize-stage\n\n', indent=False)

        self.add_entrypoint()

        if self.matrix:
            self.export_dockerfile_matrix()
        else:
            self.export_to_dockerfile()

    @log_function_call
    def create(self):
        self.create_base_stage()
        self.create_system_stage()
        if self.spack_install:
            self.create_spack_stage()
        self.create_finalize_stage()
