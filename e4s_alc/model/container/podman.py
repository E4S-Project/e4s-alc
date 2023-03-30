import os
import subprocess
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
            process = subprocess.Popen(['podman', 'info'],
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
            process_out, process_err = process.communicate()
            if process_err:
                print('Failed to connect to Podman client')
                return

            p_out = process_out.decode('utf-8')
            print(p_out)

            with podman.PodmanClient(base_url=uri) as client:
                version = client.version()
                print("Release: ", version["Version"])


        except podman.errors.exceptions.APIError:
            print('Failed to connect to Podman client')
            return
        
        self.is_active = True
