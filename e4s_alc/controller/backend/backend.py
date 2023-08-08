class ContainerBackend:
    """
    A class used to represent the backend operations on different containers.
    """
    
    def __init__(self):
        """
        Constructs all the necessary attributes for the container backend object.
        """
        self.program = None

    def pull(self, image, tag):
        """
        Pulls a specific image with a particular tag

        Parameters:
            image (str): The image to be pulled
            tag (str): Tag of the image to be pulled

        """
        pass

    def get_os_release(self, image, tag):
        """
        Gets the operating system release for a specific image using a specific tag.

        Parameters:
            image (str): The image whose OS release is to be retrieved
            tag (str): Tag of the image
        
        """
        pass
