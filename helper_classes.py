from dateutil import parser

class TimeRange:
    def __init__(self,rng):
        self.times = [parser.parse(item) for item in rng]
        self.i = 0
        self.times = sorted(self.times)
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.i < len(self.times):
            i = self.i
            self.i += 1
            return self.times[i]
        else:
            self.i = 0
            raise StopIteration()

    def __str__(self):
        return str(self.times)

    @property
    def start(self):
        return self.times[0]

    @property
    def end(self):
        return self.times[-1]