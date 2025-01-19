# a class to contain the details of preprocessing such as cropping, resizing, reformatting.
class ProcessingDetail:
    def __init__(self):
        self.resized = False
        self.reformatted = False
        self.cropping = False
