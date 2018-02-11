test_arr = {}

class Test:
    def __init__(self, value):
        self.value = value
        self.fart = "ASD"

    @staticmethod
    def register():
        test_arr["test"] = Test


Test.register()

x = test_arr['test'](value="www")

print(x.value)
print(x.fart)