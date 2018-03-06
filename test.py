class tester:
    def __init__(self,s):
        self.data = s
    def __truediv__(self, key):
        return tester("{}{}".format(self.data,key))
    def __sub__(self,key):
        return tester(self.data.replace(key,""))
    def __str__(self):
        return self.data

if __name__ == "__main__":
    t = tester("hello")
    print(((t / "world") - "owo") / "asdf")