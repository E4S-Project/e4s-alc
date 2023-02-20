class Controller():
    def __init__(self, module_name):
        self.module_name = module_name
        self.client = None
        self.is_active = False
