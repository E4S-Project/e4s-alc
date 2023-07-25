import logging
import textwrap

logger = logging.getLogger('core')

class Image():
    def __init__(self, os_release):
        logger.info("Initializing Image")
        self.id = None
        self.version = None
        self.packages = None
        self.pkg_manager_commands = None
        self.update_cert_command = None

        self.read_os_release(os_release)

    def read_os_release(self, os_release):
        logger.debug("Reading OS release")
        self.id = os_release['ID']
        self.version = os_release['VERSION_ID']

    def get_update_certificate_command(self):
        logger.debug("Getting update certificate command")
        return self.update_cert_command

    def convert_cert_path(self, cert_path):
        logger.debug(f"Converting certificate path: {cert_path}")
        filename = cert_path.split('/')[-1]
        if filename.endswith('.pem') or filename.endswith('.crt') or filename.endswith('.cer'):
            filename = filename.split('.')[0] + '.crt'
            new_path = f'{self.cert_location}{filename}'
            return new_path

    def wrap_packages(self, packages):
        logger.debug("Textwrapping packages")
        return textwrap.fill(packages, width=70, break_long_words=False, break_on_hyphens=False).replace('\n', ' \\\n\t\t')
