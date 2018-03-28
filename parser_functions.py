import os,sqlite3
from shapely.wkt import loads,dumps
from pathlib import Path
from tinydb import TinyDB,Query
dbname = os.environ["DBNAME"]
directory = Path(__file__).parent.resolve() #pylint: disable=no-member
def get_all_shapes():
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    c.execute("select name,wkt from jobs")
    r = c.fetchall()
    c.close()
    return r

def get_data_from_job(name,time_range):
    data = []
    for fname in (directory / "data" / name).glob("{}/*".format(name)):
        db = TinyDB(str(fname / "db.json"))


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




