from e4s_alc.model.container.docker import DockerController
from e4s_alc.model.container.podman import PodmanController
from e4s_alc.model.container.singularity import SingularityController

SUPPORTED_BACKENDS = {
        'docker': DockerController, 
        'podman': PodmanController,
        'singularity': SingularityController
}
