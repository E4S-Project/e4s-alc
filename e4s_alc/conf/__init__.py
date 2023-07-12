import os

def get_modules_conf():
    directory_location = os.path.dirname(os.path.abspath(__file__))
    module_yaml_location = os.path.join(directory_location, 'modules.yaml')
    return module_yaml_location
