import os,sqlite3
from shapely.wkt import loads,dumps
from pathlib import Path
from tinydb import TinyDB,Query
from helper_classes import TimeRange
dbname = os.environ["DBNAME"]
directory = Path(__file__).parent.resolve() #pylint: disable=no-member
def get_all_shapes():
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    c.execute("select name,wkt from jobs")
    r = c.fetchall()
    c.close()
    return r

def timesearch_function(tr,s):
    if s != []:
        return TimeRange(s) in TimeRange(tr)
    else:
        return False

def get_data_from_job(name,time_range):
    print(TimeRange(time_range))
    data = []
    ttest = lambda s: timesearch_function(time_range,s)
    for fname in (directory / "data").glob("{}/*".format(name)):
        print(fname)
        db = TinyDB(str(fname / "db.json"))
        o = db.search(Query().times.test(ttest))
        data += o
    return data


def geosearch(query):
    out = []
    obj = loads(query)
    for item in get_all_shapes():
        if obj.intersects(loads(item[1])):
            out.append([item[0],item[1]])
    return out

def perform_search(src):
    out = []
    if src['wkt'] != '':
        out = geosearch(src['wkt'])
    return out




