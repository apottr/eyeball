import os,sqlite3,json,pyproj,math
from shapely.wkt import loads,dumps
from shapely.geometry import shape
from shapely.ops import transform
from pathlib import Path
from tinydb import TinyDB,Query
from helper_classes.helper_classes import TimeRange
from functools import partial

dbname = os.environ["DBNAME"]
directory = Path(__file__).parent.parent.resolve() #pylint: disable=no-member
dbf = str(directory / "databases" / "lookups.db")
def get_all_job_shapes():
    conn = sqlite3.connect(str(directory / "databases" / dbname))
    c = conn.cursor()
    c.execute("select name,wkt from jobs")
    r = c.fetchall()
    c.close()
    return r

def get_all_geonames_shapes():
    conn = sqlite3.connect(dbf)
    c = conn.cursor()
    c.execute("select geonameid,wkt from geonames_shapes")
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

def reproject_from_wgs84(shape):
    project = partial(pyproj.transform,pyproj.Proj(init="epsg:4326"),pyproj.Proj(init="epsg:3857"))
    return transform(project,shape)

def geosearch(query):
    out = []
    obj = loads(query)
    for item in get_all_job_shapes():
        if obj.intersects(loads(item[1])):
            out.append([item[0],item[1]])
    for item in get_all_geonames_shapes():
        jtem = reproject_from_wgs84(loads(item[1]))
        if jtem.geom_type == "MultiPolygon":
            for geom in jtem.geoms:
                if (not math.isnan(geom.area)) and obj.intersects(geom):
                    out.append([item[0],jtem.wkt])
                    break
        elif jtem.area != "nan":
            if obj.intersects(jtem):
                out.append([item[0],jtem.wkt])
    return out

def perform_search(src):
    out = []
    if src['wkt'] != '':
        out = geosearch(src['wkt'])
    return out




