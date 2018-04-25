import sqlite3,os
from .globals import directory,sources_db

def check_if_source_is_used(name):
    conn = sqlite3.connect(sources_db)
    c = conn.cursor()
    c.execute('select loctag from sources where name=?',(name,))
    r = c.fetchall()
    tag = r[0][0]
    if "," in tag:
        tag = tag.split(",")
    o = []
    if isinstance(tag,list):
        for t in tag:
            d = c.execute('select * from jobs where tags like ?',(f"%{t}%",))
            o.append(1 if len(d.fetchall()) > 0 else 0)
    else:
        d = c.execute('select * from jobs where tags like ?',(f"%{tag}%",))
    return 1 in o

def get_sources():
    out = []
    conn = sqlite3.connect(sources_db)
    c = conn.cursor()
    c.execute("select * from sources")
    r = c.fetchall()
    if len(r) != 0:
        for item in r:
            out.append({
                "name": item[0],
                "snippet": item[1],
                "tags": item[2],
                "selector": item[3]
            })
    return out

def add_source(src):
    conn = sqlite3.connect(sources_db)
    c = conn.cursor()
    try:
        c.execute('insert into sources values (?,?,?,?)',(src["name"],src["command"],src["tag"],src["selector"]))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(e)
        return False


def delete_source(name):
    conn = sqlite3.connect(sources_db)
    c = conn.cursor()
    c.execute('delete from sources where name=?',(name,))
    conn.commit()
    conn.close()

def sources_from_csv(lst):
    conn = sqlite3.connect(sources_db)
    c = conn.cursor()
    c.executemany("insert into sources values (?,?,?,?)",[i for i in lst][1:])
    conn.commit()
    conn.close()