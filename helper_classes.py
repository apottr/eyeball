from dateutil import parser
import datetime

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
            return self[i]
        else:
            self.i = 0
            raise StopIteration()

    def __str__(self):
        return str(self.times)

    def __getitem__(self,b):
        return self.times[b]

    def __contains__(self,b):
        state = True
        if isinstance(b,TimeRange):
            for item in b:
                state = item in self
                if not state:
                    return state
            return state
        elif isinstance(b,datetime.datetime):
            return (self.start <= b and self.end >= b)
        else:
            d = parser.parse(b)
            return d in self
    
    @property
    def start(self):
        return self[0]

    @property
    def end(self):
        return self[-1]