class BackendFailedError(Exception):
    def __init__(self, backend, command):
        self.message = f'Your {backend} backend failed to run the command `{command}`.'
        super().__init__(self.message)

class BackendMissingError(Exception):
    def __init__(self, message='You will need to install a container backend for this program to work'):
        self.message = message
        super().__init__(self.message)

class YAMLNotFoundError(Exception):
    def __init__(self, filename):
        self.message = f'Failed to find YAML file: {filename}.'
        super().__init__(self.message)
