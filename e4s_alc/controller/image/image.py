import textwrap
from e4s_alc.util import log_function_call

class Image():
    """
    A helper class to manage OS image metadata and related operations.
    """

    def __init__(self, os_release):
        """
        Initializes the Image object with the provided OS release information.
        """
        self.id = None
        self.version = None
        self.packages = None
        self.pkg_manager_commands = None
        self.update_cert_command = None
        self.read_os_release(os_release)

    @log_function_call
    def read_os_release(self, os_release):
        """
        Reads and sets the OS release information.

        Args:
            os_release (dict): A dictionary containing the OS release information.
        """
        self.id = os_release['ID']
        self.version = os_release['VERSION_ID']

    @log_function_call
    def get_update_certificate_command(self):
        """
        Returns the command to update the certificate.
        """
        return self.update_cert_command

    @log_function_call
    def convert_cert_path(self, cert_path):
        """
        Converts the certificate path to use the correct file extension.

        Args:
            cert_path (str): The original certificate file path.

        Returns:
            str: The new certificate file path.
        """
        filename = cert_path.split('/')[-1]
        if filename.endswith('.pem') or filename.endswith('.crt') or filename.endswith('.cer'):
            filename = filename.split('.')[0] + '.crt'
            new_path = f'{self.cert_location}{filename}'
            return new_path

    @log_function_call
    def wrap_packages(self, packages):
        """
        Wraps the provided package list to 70 characters width.

        Args:
            packages (str): A string containing the package list.

        Returns:
            str: Properly wrapped package list string.
        """
        return textwrap.fill(packages, width=70, break_long_words=False, break_on_hyphens=False).replace('\n', ' \\\n\t    ')
