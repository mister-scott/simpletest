class DynamicClass:
    def __init__(self, data_dict):
        for key, value in data_dict.items():
            setattr(self, key, value)

    def update(self, data_dict):
        self.__init__(data_dict)

    def index(self):
        return [attr for attr in dir(self) if not callable(get attr(self, attr)) and not attr.startswith("__")]