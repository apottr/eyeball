import sqlite3,os,rpyc
from crontab import CronTab
from .globals import directory,sources_db,rem_port

cron = CronTab(user=True)
pybin = directory / "bin" / "python"

def lookup_by_tag(tag):
    conn = sqlite3.connect(sources_db)
    c = conn.cursor()
    c.execute('select * from sources where loctag like ?',(f"%{tag}%",))
    return c.fetchall()

def job_pauser(x,rem_server):
    c = rpyc.connect(rem_server,rem_port)
    c.root.job_pauser(x)

def get_tags():
    out = {}
    conn = sqlite3.connect(sources_db)
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

def sh_generator(tag,name,rc):
    return rc.root.sh_generator(lookup_by_tag(tag),name)

def add_job(src,rem_server):
    rc = rpyc.connect(rem_server,rem_port)
    conn = sqlite3.connect(sources_db)
    c = conn.cursor()
    sh = sh_generator(src["tags"],src["name"],rc)
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
    v = rc.root.add_sh_to_cron(src["name"],sh,sch)
    print("{} is valid: {}".format(src["name"],v))
    if v:
        cron.write()
    return v

def get_jobs():
    out = []
    conn = sqlite3.connect(sources_db)
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

def check_cron(rem_server):
    jobs = get_jobs()
    c = rpyc.connect(rem_server,rem_port)
    c.root.check_cron(jobs)

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

def delete_job(name,rem_server):
        rc = rpyc.connect(rem_server,rem_port)
        rc.root.del_job(name)
        conn = sqlite3.connect(sources_db)
        c = conn.cursor()
        c.execute('delete from jobs where name=?',(name,))
        conn.commit()
        conn.close()