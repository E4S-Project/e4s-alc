import unittest
from e4s_alc.mvc.controller import Controller
from e4s_alc import logger, E4S_ALC_HOME

logger.set_log_level("FATAL")

ASSETS_DIRECTORY = E4S_ALC_HOME + "/tests/assets/"

class ControllerTests(unittest.TestCase):

    def test_read_args_file(self):
        controller = Controller("test")
        data = controller.read_args_file(ASSETS_DIRECTORY + "testconfig.json")
        self.assertEqual(data['image'], 'ubuntu:22.04')
        self.assertEqual(data['name'], 'test-configuration-file')
        self.assertEqual(data['spack'], True)
        self.assertEqual(data['spack-packages'], ['kokkos', 'raja'])
        self.assertEqual(data['os-packages'], ['neovim', 'valgrind'])

    def test_expand_tarball_url(self):
        image_path = ASSETS_DIRECTORY + "image.test"
        controller = Controller("test")
        controller.expand_tarball("https://www.google.com", image_path)
        self.assertEqual(controller.commands, ['curl -O https://www.google.com', 'tar xf www.google.com -C ' + image_path , 'mv www.google.com /tmp/www.google.com'])

    def test_expand_tarball_path(self):
        image_path = ASSETS_DIRECTORY + "image.test"
        tarball_path = ASSETS_DIRECTORY + "test.tar"
        controller = Controller("test")
        controller.expand_tarball(tarball_path, image_path)
        self.assertEqual(controller.commands, ['tar xf /tmp/assets/test.tar -C ' + image_path])
        self.assertEqual(controller.mounts, ['/home/fdeny/Work/e4s-alc/tests/assets:/tmp/assets'])

    def test_add_ubuntu_commands(self):
        controller = Controller("test")
        controller.add_ubuntu_package_commands(['neovim', 'valgrind'])
        self.assertEqual(controller.commands, ['apt-get update', 'apt-get install -y build-essential ca-certificates coreutils curl environment-modules gfortran git gpg lsb-release vim python3 python3-distutils python3-venv unzip zip cmake neovim valgrind'])

    def test_add_centos_commands(self):
        controller = Controller("test")
        controller.os_release['VERSION'] = '8'
        controller.add_centos_package_commands(['neovim', 'valgrind'])
        self.assertEqual(controller.commands, ["yum -y --disablerepo '*' --enablerepo=extras swap centos-linux-repos centos-stream-repos", 'yum -y distro-sync', 'yum update -y', 'yum install epel-release -y', 'yum --enablerepo epel groupinstall -y "Development Tools"', 'yum --enablerepo epel install -y curl findutils gcc-c++ gcc gcc-gfortran git gnupg2 hostname iproute redhat-lsb-core make patch python3 python3-pip python3-setuptools unzip cmake vim neovim valgrind', 'python3 -m pip install boto3'])

    def test_add_sles_commands(self):
        controller = Controller("test")
        controller.add_sles_package_commands(['neovim', 'valgrind'])
        self.assertEqual(controller.commands, ['zypper update', 'zypper install -y curl gzip tar python3 python3-pip gcc gcc-c++ gcc-fortran patch make gawk xz cmake bzip2 vim neovim valgrind'])

    def test_add_spack_commands(self):
        controller = Controller("test")
        controller.add_spack_package_commands(['kokkos', 'petc'])
        self.assertEqual(controller.commands, ['spack install --yes-to-all kokkos', 'spack install --yes-to-all petc'])

    def test_install_spack(self):
        controller = Controller("test")
        controller.environment['PATH'] = 'test'
        controller.install_spack()
        self.assertEqual(controller.commands,['curl -OL https://github.com/spack/spack/releases/download/v0.19.1/spack-0.19.1.tar.gz', 'gzip -d /spack-0.19.1.tar.gz', 'tar -xf /spack-0.19.1.tar', 'rm /spack-0.19.1.tar', 'mv /spack-0.19.1 /spack', '. /spack/share/spack/setup-env.sh', 'echo export PATH=test:/spack/bin >> ~/.bashrc'] )
