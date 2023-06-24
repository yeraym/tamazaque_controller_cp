import os


class Menu:
    def __init__(self):
        self.configs = []

    def list_configs(self):
        files = os.listdir()
        for file in files:
            if '.' in file and file.split('.')[1]=='json':
                print(file)