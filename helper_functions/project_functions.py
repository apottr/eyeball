import sqlite3,os
from pathlib import Path

def get_x_from_project(projname,x):
    fields = ["name","sources","datasets","rules"]
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    c.execute("select * from projects where name=?",(projname,))
    r = c.fetchone()
    if len(r) != 0:
        return [{fields[x]: item} for item in r[x].split(";")]
    return []

def get_projects():
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    c.execute("select * from projects")
    r = c.fetchall()
    out = []
    if len(r) != 0:
        for item in r:
            out.append({
                "name": item[0]
            })
    return out

def add_project(f):
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    c.execute("insert into projects values (?,?,?,?)",(f["name"],f["sources"],"",""))
    conn.commit()
    conn.close()

def get_sources_for_project(projname):
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    c.execute("select * from projects inner join jobs on projects.sources = jobs.name where projects.name = ?",(projname,))
    r = c.fetchone()
    out = []
    if len(r) != 0:
        out.append({
            "project.name": r[0],
            "job.name": r[1],
            "job.schedule": r[6]
        })
    return out

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

if __name__ == "__main__":
    from globals import directory,dbname
    p = get_projects()
    print(p)
    print(get_sources_for_project(p[0]["name"]))
else:
    from .globals import directory,dbname
