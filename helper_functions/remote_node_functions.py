from tinydb import TinyDB,Query
from .globals import directory
import rpyc

dbname = str(directory / "databases" / "nodes.db")

def check_is_online(hostname):
    try:
        c = rpyc.connect(hostname,18816)
        c.close()
        return True
    except Exception:
        return False


def get_nodes():
    db = TinyDB(dbname)
    out = []
    for row in db:
        d = row
        d["online"] = check_is_online(row["host"])
        out.append(d)
    return out

def add_node(f):
    db = TinyDB(dbname)
    o = {
        "name": f["name"],
        "host": f["host"],
        "loc": f["location"],
        "online": False
    }
    db.insert(o)
    


if __name__ == "__main__":
    get_nodes()