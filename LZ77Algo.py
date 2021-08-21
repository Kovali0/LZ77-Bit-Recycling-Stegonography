class LZ77:
    def __init__(self):
        self.file_path = ''
        self.file = ''
        self.content = []

    def compressFile(self, file_path):
        self.file_path = file_path
        self.file = open(file_path, "r")
        self.content = self.file.read()
        print(self.content)
