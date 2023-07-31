import logging

logger = logging.getLogger('core')

class ContainerBackend():
    def __init__(self):
        logger.info("Initializing ContainerBackend")
        self.program = None

    def pull(self, image, tag):
        logger.debug(f"Pulling image {image} with tag {tag}")

    def get_os_release(self, image, tag):
        logger.debug(f"Getting OS release for image {image} with tag {tag}")
