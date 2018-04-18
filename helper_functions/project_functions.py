import sqlite3,os
from pathlib import Path
from .globals import directory,dbname

def get_x_from_project(projname,x):
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    c.execute("select * from projects where name=?",(projname,))
    r = c.fetchone()
    if len(r) != 0:
        return r[x].split(";")
    return []

def add_project(f):
    pass

def get_sources_for_project(projname):
    return get_x_from_project(projname,1)

def get_datasets_for_project(projname):
    return get_x_from_project(projname,2)

def get_rules_for_project(projname):
    return get_x_from_project(projname,3)

def delete_project(name):
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    c.execute('delete from projects where name=?',(name,))
    conn.commit()
    conn.close()