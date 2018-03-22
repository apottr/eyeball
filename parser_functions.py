import os,sqlite3
from shapely.wkt import loads,dumps

dbname = os.environ["DBNAME"]

def get_all_shapes():
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    c.execute("select name,wkt from jobs")
    r = c.fetchall()
    c.close()
    return r

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




