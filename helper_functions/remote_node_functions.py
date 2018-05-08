from tinydb import TinyDB,Query
from .globals import directory,rem_port
from .job_functions import check_cron
import rpyc

dbname = str(directory / "databases" / "nodes.db")

def check_is_online(hostname):
    try:
        c = rpyc.connect(hostname,rem_port)
        c.close()
        return True
    except Exception:
        return False


def get_nodes():
    db = TinyDB(dbname)
    out = []
    if len(db) != 0:
        for row in db:
            d = row
            d["online"] = check_is_online(row["host"])
            out.append(d)

    return out

def remotes_check_cron():
    db = TinyDB(dbname)
    if len(db) == 0:
        return
    else:
        for row in db:
            if check_is_online(row["host"]):
                check_cron(row["host"])

def add_node(f):
    db = TinyDB(dbname)
    o = {
        "name": f["name"],
        "host": f["host"],
        "loc": f["location"],
        "online": False
    }
    db.insert(o)
    
def delete_node(name):
    db = TinyDB(dbname)
    d = db.search(Query().name == name)
    db.remove(doc_ids=[i.doc_id for i in d])

if __name__ == "__main__":
    get_nodes()