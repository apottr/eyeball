import sqlite3,os
from pathlib import Path
from crontab import CronTab

dbname = os.environ["DBNAME"]
directory = Path(__file__).parent.resolve() #pylint: disable=no-member
cron = CronTab(user=True)
pybin = directory / "bin" / "python"

def init_db():
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    try:
        c.execute('select * from sources')
    except sqlite3.OperationalError:
        c.execute('create table sources (name text, command text, loctag text)')
    try:
        c.execute('select * from jobs')
    except sqlite3.OperationalError:
        c.execute('create table jobs (name text, tags text, schedule text, wkt string)')

    c.close()

def add_source(src):
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    try:
        c.execute('insert into sources values (?,?,?)',(src["name"],src["command"],src["tag"]))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(e)
        return False

def add_job(src):
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    sh = sh_generator(src["tags"],src["name"])
    sch = ""
    if src["sch_mhd"] == "m":
        sch = "*/{} * * * *".format(src["sch_n"])
    elif src["sch_mhd"] == "h":
        sch = "0 */{} * * *".format(src["sch_n"])
    elif src["sch_mhd"] == "d":
        sch = "0 0 */{} * *".format(src["sch_n"])
    try:
        c.execute('insert into jobs values (?,?,?,?)',(src["name"],src["tags"],sch,src["wkt"]))
        conn.commit()
        conn.close()
    except Exception as e:
        print(e)
    """if src["picker"] == "tag":
        v = add_sh_to_cron(src["name"],sh,sch)
    elif src["picker"] == "man":
        v = add_job_by_hand(src["script"],src["name"],sch)"""
    v = add_sh_to_cron(src["name"],sh,sch)
    print("{} is valid: {}".format(src["name"],v))
    if v:
        cron.write()
    return v

def lookup_by_tag(tag):
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    c.execute('select * from sources where loctag like ?',("%{}%".format(tag),))
    return c.fetchall()

def get_tags():
    out = {}
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    c.execute("select loctag from sources")
    r = c.fetchall()
    if len(r) != 0:
        for item in r:
            x = item[0].split(",")
            for tag in x:
                if tag in out:
                    out[tag] += 1
                else:
                    out[tag] = 1
    return out

def get_sources():
    out = []
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    c.execute("select * from sources")
    r = c.fetchall()
    if len(r) != 0:
        for item in r:
            out.append({
                "name": item[0],
                "snippet": item[1],
                "tags": item[2]
            })
    return out

def get_jobs():
    out = []
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    c.execute("select * from jobs")
    r = c.fetchall()
    if len(r) != 0:
        for item in r:
            out.append({
                "name": item[0],
                "tags": item[1],
                "schedule": item[2]
            })
    return out

def check_cron():
    jobs = get_jobs()
    d = directory / "shell_files"
    for job in jobs:
        if len(list(cron.find_comment(job["name"]))) == 0:
            fname = (d / job["name"].replace(" ","_")).with_suffix(".sh")
            j = cron.new(command="sh {}".format(fname),comment=job["name"])
            j.setall(job["schedule"])
    if len(list(cron.find_command(str(directory / "processor")))) == 0:
        x = cron.new(command=("{} {}".format(pybin,(directory / "processor").with_suffix(".py"))))
        x.setall("0 * * * *")
    print(cron)

def sh_generator(tag,name):
    lines = []
    f = lookup_by_tag(tag)
    if len(f) != 0:
        for entry in f:
            d = (directory / "data" / name.replace(" ","_") / entry[0])
            d.mkdir(parents=True,exist_ok=True)
            lines.append("{0} > {2}/$(date +%s) #{1}".format(entry[1],entry[0],d))
    return lines

def add_sh_to_cron(name,sh,schedule):
    out = "\n\n".join(["#!/bin/sh",*sh])
    d = directory / "shell_files"
    fname = (d / name.replace(" ","_")).with_suffix(".sh")
    f = open(fname,"w+")
    f.write(out)
    j = cron.new(command="sh {}".format(fname),comment=name)
    j.setall(schedule)
    v = j.is_valid()
    #v = True
    if v:
        return j
    else:
        os.remove(fname)
        return False

def add_job_by_hand(script,name,sched):
    d = directory / "shell_files"
    fname = (d / name.replace(" ","_")).with_suffix(".sh")
    f = open(fname,"w+")
    f.write(script)
    j = cron.new(command="sh {}".format(fname),comment=name)
    j.setall(sched)
    v = j.is_valid()
    if v:
        return j
    else:
        os.remove(fname)
        return False

def delete_job(name):
        try:
            os.remove("shell_files/{}.sh".format(name.replace(" ","_")))
        except Exception as e:
            print(e)
        cron.remove_all(comment=name)
        d = (directory / "data" / name.replace(" ","_"))
        for f in d.iterdir():
            if f.is_dir():
                for x in f.iterdir():
                    os.remove(x)
                f.rmdir()
            else:
                os.remove(f)
        d.rmdir()
        conn = sqlite3.connect(dbname)
        c = conn.cursor()
        c.execute('delete from jobs where name=?',(name,))
        conn.commit()
        conn.close()
        cron.write()

def delete_source(name):
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    c.execute('delete from sources where name=?',(name,))
    conn.commit()
    conn.close()

def sources_from_csv(lst):
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    c.executemany("insert into sources values (?,?,?)",[i for i in lst][1:])
    conn.commit()
    conn.close()