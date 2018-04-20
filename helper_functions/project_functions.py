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
    c.execute("select * from projects inner join jobs on projects.sources like '%' || jobs.name || '%' where projects.name = ?",(projname,))
    r = c.fetchall()
    out = []
    if len(r) != 0:
        for item in r:
            out.append({
                "project.name": item[0],
                "job.name": item[4],
                "job.schedule": item[6]
            })
    return out

def set_x_for_project(projname,lst,x):
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    c.execute("update projects set {}=?".format(x),(";".join(lst),))
    conn.commit()
    conn.close()

def get_jobs_for_project(projname,alljbs):
    jbs = []
    pjbs = [item["job.name"] for item in get_sources_for_project(projname)]
    for item in [item["name"] for item in alljbs]:
        if item in pjbs:
            jbs.append({"name": item, "checked": True})
        else:
            jbs.append({"name": item, "checked": False})
    return jbs

def set_sources_for_project(projname,lst):
    set_x_for_project(projname,lst,"sources")

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
