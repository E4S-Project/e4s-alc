from e4s_alc.model.container.docker import DockerController
from e4s_alc.model.container.podman import PodmanController

SUPPORTED_BACKENDS = {
        'docker': DockerController, 
        'podman': PodmanController
}
