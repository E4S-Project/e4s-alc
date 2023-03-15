from e4s_alc.mvc.controller import Controller

class PodmanController(Controller):
    def __init__(self):
        super().__init__('PodmanController')

        try:
            import podman
        except ImportError:
            print('Failed to find Podman python library')
            return

        try:
#            self.client = podman.PodmanClient(base_url='ssh://core@localhost:49363/run/user/501/podman/podman.sock')
#            print(self.client.version())

            uri = 'unix:///run/user/501/podman/podman.sock'

            with podman.PodmanClient(base_url=uri) as client:
                version = client.version()
                print("Release: ", version["Version"])


        except podman.errors.exceptions.APIError:
            print('Failed to connect to Podman client')
            return
        
        self.is_active = True
