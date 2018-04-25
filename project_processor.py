from helper_functions.project_functions import * #pylint:disable=W0614
from pathlib import Path
from tinydb import TinyDB,Query
from nltk.corpus import stopwords as sw
import re,json,nltk

directory = Path(__file__).parent.resolve() #pylint:disable=no-member
nltk.data.path.append(str(directory / "nltk_data_storage"))
stopwords = set(sw.words('english'))
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

def rem_stopwords(lst):
    out = []
    for word in lst:
        if word not in stopwords:
            out.append(word)
    return out

def match_sentence(doc,rx):
    out = []
    for item in doc:
        if isinstance(item,list):
            out.append(match_sentence(item,rx))
        else:
            m = re.search(rx,item)
            out.append(bool(m))
    return out

def match_rule_item_in_db(db,item):
    out = []
    if "before" in item:
        before = int(item["before"])
    if "after" in item:
        after = 1 if int(item["after"]) == 0 else int(item["after"])
    for row in db:
        idx = 0
        toggle = True
        for jtem in row["entites"]:
            o = match_sentence(jtem,item["rule"])
            for i in range(len(o)):
                for j in range(len(o[i])):
                    if o[i][j]:
                        out.append({"data": rem_stopwords(jtem[i][j-before:j+after]),
                                    "time": row["times"][idx],
                                    "filename": row["filename"],
                                    "idx": j})
        if toggle:
            idx += 1
            toggle = False
        else:
            toggle = True
    return out
        

def match_rule_to_db(fname,rule):
    r = json.loads(rule)
    db = TinyDB(fname)
    o = match_rule_item_in_db(db,r)
    return o

if __name__ == "__main__":
    projname = "testproj"
    create_table(projname)
    l = get_db_fnames_from_project(projname)
    rules = get_rules_for_project(projname)
    out = []
    for k in l:
        for rule in rules:
            h = match_rule_to_db(k,json.dumps(rule))
            if len(h) != 0:
                out += h
    insert_rule_datas(projname,out)