class BaseService:

    def __init__(self, image):
        self.image = image

    def execute(self):
        raise Exception("To be implemented")
