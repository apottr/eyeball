from helper_functions.project_functions import * #pylint:disable=W0614
from pathlib import Path
from tinydb import TinyDB,Query

directory = Path(__file__).parent.resolve() #pylint:disable=no-member

def get_db_fnames_from_project(projname):
    out = []
    for job in get_sources_for_project(projname):        
        p = (directory / "data" / job["job.name"].replace(" ","_"))
        for item in p.glob("*/db.json"):
            out.append(str(item))
    return out

def get_first_from_db(fname):
    db = TinyDB(fname)
    print(db.get(doc_id=1))

if __name__ == "__main__":
    l = get_db_fnames_from_project("testproj")
    for fname in l:
        get_first_from_db(fname)