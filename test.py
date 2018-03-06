class tester:
    def __init__(self,s):
        self.data = s
    def __truediv__(self, key):
        return "{}{}".format(self.data,key)
    def __sub__(self,key):
        return self.data.replace(key,"")

if __name__ == "__main__":
    t = tester("hello")

    print(t / "world")
    print(t - "he")



