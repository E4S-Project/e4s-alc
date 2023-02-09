import os
import sys
import click
import docker
import datetime

import e4s_alc
from e4s_alc.database.edit import read_entry, modify_entry

# ==============
# Add Command
# ==============

@click.command()
@click.option('-n', '--name', required=True, help='[Required] The name of the output image')
@click.option('-p', '--package', help='The spack packages to install', multiple=True)
@click.option('-a', '--os-package', help='The apt/yum packages to install', multiple=True)
@click.option('-c', '--copy', help='The directory to copy to the image', multiple=True, default=[])
def add(name, package, os_package, copy):
    print()
    click.secho('E4S-ALC', fg='green')
    print('name: ', name)
    print('packages: ', list(package))
    print('os-packages: ', list(os_package))
    print('Copy: ', list(copy))
    print()

    # Get docker client
    client = docker.from_env(timeout=600)

    # Get image
    image = client.images.get(name)

    # Parse OS release
    os_release_dict = {}
    os_release = client.containers.run(image, 'cat /etc/os-release', remove=True)
    os_release_parsed = os_release.decode().replace('\"', '').splitlines()
    for item in os_release_parsed:
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
            'python3', 'python3-pip', 'python3-setuptools', 'unzip', 'vim', 'cmake'
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

    # Check if spack exists
    try:
        spack = client.containers.run(image, 'ls /spack/bin', remove=True)
    except docker.errors.ContainerError:
        spack = False 
        if not os_package and not copy:
            print('Spack was not found on this image')
            return
       
    # Spack packages
    if spack:
        for pack in package:
            commands.append('spack install {}'.format(pack))
    
    # Make environment
    env = {
        'PYTHONUNBUFFERED': '1',
        'DEBIAN_FRONTEND': 'noninteractive',
        'PATH': '{}{}'.format(env_dict['PATH'], ':/spack/bin')
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

    # Get previous entry
    name, os_tag, prev_packages, date = read_entry(name)

    if prev_packages == '':
        prev_packages = []

    # Modify database entry 
    now = datetime.datetime.now()
    modify_entry(
        name,
        os_tag,
        ' '.join(list(package) + prev_packages),
        str(now)             
    )
