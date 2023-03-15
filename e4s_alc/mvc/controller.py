class Controller():
    def __init__(self, module_name):
        self.module_name = module_name
        self.client = None
        self.is_active = False
        self.image = None
        self.image_os = None
        self.image_tag = None
        self.os_release = {}
        self.environment = {}
        self.commands = []
        self.mounts = []

    def pull_image(self, image):
        pass

    def parse_os_release(self):
        pass

    def parse_environment(self):
        pass

    def add_ubuntu_package_commands(self, os_packages):
        pass
    
    def add_centos_package_commands(self, os_packages):
        pass

    def init_image(self, image):
        pass

    def mount_and_copy(self, host_path, image_path):
        pass

    def add_system_package_commands(self, os_packages):
        pass

    def execute_build(self, name):
        pass
