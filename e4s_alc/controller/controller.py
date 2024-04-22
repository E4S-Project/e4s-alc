from e4s_alc.util import log_function_call, log_info, log_error
from e4s_alc.controller.image import UbuntuImage, RhelImage, RockyImage
from e4s_alc.controller.backend import DockerBackend, PodmanBackend, SingularityBackend

class Controller:
    """
    Class for managing container images and performing operations with them using specified backend.
    """

    _image_os_dict = {'ubuntu': UbuntuImage,
                      'rhel': RhelImage,
                      'rocky': RockyImage}
    _image_cache = {}

    @log_function_call
    def __init__(self, backend_type, base_image, repull=None):
        """
        Initializes a Controller instance.

        Args:
            backend_type (str): Type of backend to be used (either `podman` or `docker`).
            base_image (str): Base image to be used.
        """
        # singularity-specific parameter
        self.repull = repull
        
        self.backend_str = backend_type
        self.backend = self._initialize_backend(backend_type)
        self.image = self._get_image_os(base_image)
        self.setup_script = '/etc/profile.d/setup-env.sh'
 
    @log_function_call
    def _initialize_backend(self, backend_type):
        """
        Initializes the backend.

        Args:
            backend_type (str): Type of backend to be initialized.

        Returns:
            DockerBackend|PodmanBackend: Instance of the initialized backend.

        Raises:
            ValueError: If `backend_type` is neither 'podman' nor 'docker'.
        """
        if backend_type == 'podman':
            return PodmanBackend()
        elif backend_type == 'docker':
            return DockerBackend()
        elif backend_type == 'singularity':
            return SingularityBackend()
        else:
            raise ValueError(f"Unsupported backend type: {backend_type}")

    @log_function_call
    def _split_image_and_tag(self, base_image):
        """
        Splits the base image into image name and tag.

        Args:
            base_image (str): Base image in 'image_name:tag' format.

        Returns:
            tuple: Tuple containing name of the image and tag.
        """
        image, tag = base_image, 'latest'
        if ':' in base_image:
            image, tag = base_image.rsplit(':', 1)

        log_info(f"Image: {image}, Tag: {tag}")
        return image, tag

    @log_function_call
    def _get_image_os(self, base_image):
        """
        Retrieves the operating system of the base image.
        
        Args:
            base_image (str): Base image from which to get the operating system.

        Returns:
            Image: Instance of the Image class corresponding to the operating system.
        """

        image, tag = self._split_image_and_tag(base_image)
        image_key = f'{image}:{tag}'

        if image_key in self._image_cache:
            log_info("Image key found in image cache.")
            self.os_release = self._image_cache[image_key]
        else:
            log_info("Image key not found in image cache. Pulling and getting os release.")
            self.os_release = self._pull_and_get_os_release(image, tag, image_key, self.repull)

        os_id = self.get_os_id()
        image_os = self._image_os_dict[os_id](self.os_release) if os_id in self._image_os_dict else None
        log_info(f"Final image_os: {image_os}")

        return image_os

    @log_function_call
    def _pull_and_get_os_release(self, image, tag, image_key, repull):
        """
        Pulls the specified image and retrieves its operating system release.

        Args:
            image (str): Image to be pulled.
            tag (str): Tag of the image.
            image_key (str): Key for accessing the image in the image cache.

        Returns:
            dict: Dictionary containing release information of the operating system.
        """
        if self.backend_str == "singularity":
            self.backend.pull(image, tag, repull)
            # Modify image variable to fit
            image = image.split('/')[-1]
        else:
            self.backend.pull(image, tag)

        log_info("Getting OS release from backend.")
        os_release = self.backend.get_os_release(image, tag)

        log_info(f"Caching OS release with image_key: {image_key}.")
        self._image_cache[image_key] = os_release

        log_info(f"Returning OS release: {os_release}.")
        return os_release

    @log_function_call
    def get_os_package_commands(self, os_packages):
        """
        Retrieves the package manager commands for the specified operating system packages.

        Args:
            os_packages (list): List of operating system package names.

        Returns:
            list: List of package manager commands for the packages.
        """
        return self.image.get_package_manager_commands(os_packages)

    @log_function_call
    def get_os_id(self):
        """
        Retrieves the ID of the operating system.

        Returns:
            str: ID of the operating system.
        """
        return self.os_release['ID']

    @log_function_call
    def get_os_id_and_version(self):
        """
        Retrieves the ID and version of the operating system.

        Returns:
            str: ID and version of the operating system.
        """
        os_id = self.get_os_id() 
        os_version = self.os_release['VERSION_ID']
        return f"{os_id}{os_version}"

    @log_function_call
    def get_certificate_locations(self, certificates):
        """
        Retrieves the locations of the specified certificates.

        Args:
            certificates (list): List of certificates.

        Returns:
            list: List of certificate locations.
        """
        return self.image.get_certificate_locations(certificates)

    @log_function_call
    def get_update_certificate_command(self):
        """
        Retrieves the command for updating certificates.

        Returns:
            str: Command for updating certificates.
        """
        return self.image.get_update_certificate_command()

    @log_function_call
    def get_env_setup_commands(self):
        """
        Generates the environment setup commands and returns them.

        Returns:
            list: List of environment setup commands.
        """
        commands = [
            f'echo ". /etc/profile.d/modules.sh" >> {self.setup_script}',
            f'echo ". /spack/share/spack/setup-env.sh" >> {self.setup_script}',
            f'echo "export MODULEPATH=\$(echo \$MODULEPATH | cut -d\':\' -f1)" >> {self.setup_script}'
        ]
        return commands

    @log_function_call
    def get_entrypoint_command(self):
        """
        Retrieves the entrypoint command.

        Returns:
            str: Entrypoint command.
        """
        commands = self.image.get_entrypoint_commands(self.setup_script)
        return ', '.join(f'"{cmd}"' for cmd in commands)
