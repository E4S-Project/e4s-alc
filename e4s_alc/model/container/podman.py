from e4s_alc.mvc.controller import Controller

class PodmanController(Controller):
    def __init__(self):
        super().__init__('PodmanController')

        try:
            import podman
        except ImportError:
            print('Error: failed to find Podman python library')
            return

        try:
            self.client = podman.PodmanClient()
            print(self.client.version())
        except podman.errors.exceptions.APIError:
            print('Error: failed to connect to Podman client')
            return
        
        self.is_active = True