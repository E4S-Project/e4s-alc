from e4s_alc.mvc.controller import Controller

class DockerController(Controller):
    def __init__(self):
        super().__init__('DockerController')
        print('Checking for Docker...')

        try:
            import docker
        except ImportError:
            print('Error: failed to find docker python library')
            return

        try:
            self.client = docker.from_env()
        except docker.errors.DockerException:
            print('Error: failed to connect to docker client')
            return
        
        self.is_active = True
