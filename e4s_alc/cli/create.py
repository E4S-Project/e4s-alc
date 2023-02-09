import os
import sys
import json
import click
import docker
import datetime

import e4s_alc
from e4s_alc.database.edit import add_entry

# ==============
# Create Command
# ==============

@click.command()
@click.option('-f', '--file', help='The file to build an image from', type=click.Path(exists=True))
@click.option('-i', '--image', help='[Required] The image you would like to build')
@click.option('-n', '--name', help='[Required] The name of the output image')
@click.option('-p', '--package', help='The spack packages to install', multiple=True)
@click.option('-a', '--os-package', help='The spack packages to install', multiple=True, default=[])
@click.option('-c', '--copy', help='The directory to copy to the image', multiple=True, default=[])
@click.option('--spack/--no-spack', help='Choose to skip installation of spack and packages', default=True)
def create(file, image, name, package, os_package, spack, copy):
    """Create a new docker image with spack packages"""
    print()
    click.secho('E4S-ALC', fg='green')
    if file:
        with open(file) as f:
            file_data = json.loads(f.read())
            image = file_data['image']
            name = file_data['name']
            package = file_data['spack-packages']
            os_package = file_data['os-packages']
            copy = file_data['copy']

    if not image or not name:
        print('If no file is specified, the -i/--image and -n/--name flag is required')
        print()
        return

    print('image: ', image)
    print('name: ', name)
    print('packages: ', list(package))
    print('os-packages: ', list(os_package))
    print('Spack: ', spack)
    print('Copy: ', list(copy))
    print()

    # Get docker client
    client = docker.from_env(timeout=600)

    # Specify image to pull
    if ':' in image:
        image_os, tag = image.split(':')
    else:
        image_os, tag = image, 'latest'

    # Pull image
    image_obj = client.images.pull(image_os, tag)

    # Parse OS release
    os_release_dict = {}
    os_release = client.containers.run(image, 'cat /etc/os-release', remove=True)
    os_release_parsed = os_release.decode().replace('\"', '').splitlines()
    for item in os_release_parsed:
        if item == '':
            continue
        item_name, item_value = item.split('=')
        os_release_dict[item_name] = item_value

    # Parse env
    env_dict = {}
    env_data = client.containers.run(image, 'printenv', remove=True)
    env_parsed = env_data.decode().replace('\"', '').splitlines()
    for item in env_parsed:
        item_name, item_value = item.split('=')
        env_dict[item_name] = item_value

    # List of commands to execute
    commands = []
   
    # OS packages (Ubuntu)
    if os_release_dict['ID'] == 'ubuntu':
        ubuntu_packages = ' '.join([
            'build-essential', 'ca-certificates', 'coreutils', 'curl',
            'environment-modules', 'gfortran', 'git', 'gpg', 'lsb-release', 'vim',
            'python3', 'python3-distutils', 'python3-venv', 'unzip', 'zip', 'cmake'
        ] + list(os_package))
        commands.append('apt-get update')
        commands.append('apt-get install -y {}'.format(ubuntu_packages))

    # OS packages (Centos)
    if os_release_dict['ID'] == 'centos':
        centos_packages = ' '.join([
            'curl', 'findutils', 'gcc-c++', 'gcc', 'gcc-gfortran', 'git',  
            'gnupg2', 'hostname', 'iproute', 'redhat-lsb-core', 'make', 'patch',
            'python3', 'python3-pip', 'python3-setuptools', 'unzip', 'cmake', 'vim'
        ] + list(os_package))

        if os_release_dict['VERSION'] == '8':
            swap_repo = 'swap centos-linux-repos centos-stream-repos'
            commands.append('yum -y --disablerepo \'*\' --enablerepo=extras {}'.format(swap_repo))
            commands.append('yum -y distro-sync')
        
        commands.append('yum update -y')
        commands.append('yum install epel-release -y')
        commands.append('yum --enablerepo epel groupinstall -y "Development Tools"')
        commands.append('yum --enablerepo epel install -y {}'.format(centos_packages))
        commands.append('python3 -m pip install boto3')

    # Spack install
    if spack:
        commands.append('git clone https://github.com/spack/spack.git /spack')
        commands.append('cd /spack && git checkout releases/v0.19')
        commands.append('. /spack/share/spack/setup-env.sh')
        commands.append('echo export PATH={}:/spack/bin >> ~/.bashrc'.format(env_dict['PATH']))

        # Spack packages
        for pack in package:
            commands.append('spack install {}'.format(pack))
        
    # Make environment
    env = {
        'PYTHONUNBUFFERED': '1',
        'DEBIAN_FRONTEND': 'noninteractive',
        'PATH': '{}{}'.format(env_dict['PATH'], ':/spack/bin' if spack else '')
    }

    # Make mounts
    mounts = []
    for copy_item in copy:
        if ':' not in copy_item:
            print('Invalid copy format. Use {host-path}:{image-path}')
            return
        host_image_path = copy_item.split(':')
        if len(host_image_path) != 2:
            print('Invalid copy format. Use {host-path}:{image-path}')
            return
        host_path, image_path = host_image_path
        abs_host_path = os.path.abspath(host_path)
        mount_item = '{}:/tmp/{}_mount_tmp'.format(abs_host_path, image_path)
        mounts.append(mount_item)
        commands.insert(0, 'cp -r /tmp/{}_mount_tmp {}'.format(image_path, image_path))
    

    # Run container
    container = client.containers.run(image, detach=True, tty=True, volumes=mounts)

    # Run commands
    for command in commands:
        click.secho('=' * 90, color='green')
        print('Command: ', command)
        click.secho('=' * 90, color='green')

        rv, stream = container.exec_run(
            'bash -c \"{}\"'.format(command),
            stream=True,
            environment=env
        )

        print()
        for chunk in stream:
            print(chunk.decode().strip())
        print()

    # Commit new image
    container.commit(name)
    container.stop()

    # Insert database entry 
    now = datetime.datetime.now()
    add_entry(
        name,
        '{}:{}'.format(image_os, tag),
        ' '.join(package),
        str(now)             
    )
