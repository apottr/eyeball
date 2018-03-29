from dateutil import parser
from datetime import datetime,timezone
import re

def check_if_epoch(t):
    try:
        int(t)
        return True
    except:
        return False

class TimeRange:
    def __init__(self,rng):
        if isinstance(rng,list):
            self.times = [parser.parse(item).astimezone() for item in rng]
        elif check_if_epoch(rng):
            self.times = [datetime.fromtimestamp(int(rng)).astimezone()]
        else:
            self.times = [parser.parse(rng).astimezone()]
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
        elif isinstance(b,datetime):
            return (self.start <= b and self.end >= b)
        else:
            d = parser.parse(b)
            return d in self
    
    @property
    def start(self):
        return self[0].astimezone()

    @property
    def end(self):
        return self[-1].astimezone()