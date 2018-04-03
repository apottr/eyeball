from parser_functions.parser_functions import get_data_from_job
from pathlib import Path
import sys,sqlite3,os

directory = Path(__file__).parent.parent.resolve() #pylint: disable=no-member
dbf = lambda x: str(directory / "databases" / "{}").format(x)

def data_handler(job,date_range):
    d = get_data_from_job(job,date_range)
    out = []
    for item in d:
        for jtem in item["entites"]:
            out += jtem
    return out

def lookup_geoname(name):
    conn = sqlite3.connect(dbf("lookups.db"))
    c = conn.cursor()
    c.execute("select * from geonames_countries where name like ? collate nocase",("%{}%".format(name),))
    r = c.fetchone()
    return {"name": r[1],
            "latitude": r[4],
            "longitude": r[5],
            "class": r[7]
            }

def lookup_geoname_batch(names):
    conn = sqlite3.connect(dbf("lookups.db"))
    c = conn.cursor()
    out = []
    for name in names:
        c.execute("select * from geonames_countries where name like ? collate nocase limit 1",("%{}%".format(name),))
        r = c.fetchone()
        print(r,name)
        if r != None:
            out.append({
                "name": r[1],
                "latitude": r[4],
                "longitude": r[5],
                "class": r[7]
            })
    return out


def get_geo_entitity(text):
    geo_entities = []
    for obj in text:
        entity = []
        for item in obj["obj"]:
            entity.append(item[0])
        geo_entities.append(" ".join(entity))
    d = lookup_geoname_batch(geo_entities)
    print(d)
        

if __name__ == "__main__":
    d = data_handler(sys.argv[1],[sys.argv[2],sys.argv[3]])
    get_geo_entitity(d)