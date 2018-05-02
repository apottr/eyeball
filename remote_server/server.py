#pylint: skip-file
import rpyc,os
from crontab import CronTab
from pathlib import Path
from tinydb import TinyDB,Query
directory = Path(__file__).parent.parent.resolve() #pylint: disable=no-member
pybin = directory / "bin" / "python"

cron = CronTab(user=True)

def job_pauser(x):
    if x == "all":
        for job in cron:
            if job.is_enabled():
                job.enable(False)
            else:
                job.enable()
    else:
        for job in cron.find_command(x):
            print(job.command)
            if job.is_enabled():
                job.enable(False)
            else:
                job.enable()
    cron.write()

def check_cron(jobs):
    d = directory / "shell_files"
    print(d,jobs)
    for job in jobs:
        if len(list(cron.find_comment(job["name"]))) == 0:
            fname = (d / job["name"].replace(" ","_")).with_suffix(".sh")
            j = cron.new(command=f"sh {fname}",comment=job["name"])
            j.setall(job["schedule"])
    if len(list(cron.find_command("data_processor"))) == 0:
        print("data processor not found")
        x = cron.new(command=("{} {}".format(pybin,(directory / "data_processor").with_suffix(".py"))))
        x.setall("0 */2 * * *")
    if len(list(cron.find_command("project_processor"))) == 0:
        print("project processor not found")
        z = cron.new(command="{} {}".format(pybin,(directory / "project_processor").with_suffix(".py")))
        z.setall("0 */3 * * *")
    print(cron)
    cron.write()

def add_sh_to_cron(name,sh,schedule):
    out = "\n\n".join(["#!/bin/sh",*sh])
    d = directory / "shell_files"
    fname = (d / name.replace(" ","_")).with_suffix(".sh")
    f = open(fname,"w+")
    f.write(out)
    j = cron.new(command=f"sh {fname}",comment=name)
    j.setall(schedule)
    v = j.is_valid()
    #v = True
    if v:
        return j
    else:
        os.remove(fname)
        return False

def del_job(name):
    try:
        os.remove("shell_files/{}.sh".format(name.replace(" ","_")))
    except Exception as e:
        print(e)
    cron.remove_all(comment=name)
    db = TinyDB(str(directory / "databases" / "sources.db"))
    g = db.search(Query().job == name)
    db.remove(doc_ids=[i.doc_id for i in g])
    d = (directory / "data" / name.replace(" ","_"))
    for f in d.iterdir(): 
        if f.is_dir():
            for x in f.iterdir():
                os.remove(x)
            f.rmdir()
        else:
            os.remove(f)
    d.rmdir()
    cron.write()

def sh_generator(tags,name):
    lines = []
    f = tags
    if len(f) != 0:
        for entry in f:
            d = (directory / "data" / name.replace(" ","_") / entry[0])
            d.mkdir(parents=True,exist_ok=True)
            lines.append("{0} > {2}/$(date +%s) #{1}".format(entry[1],entry[0],d))
    return lines

def create_source_config(sources,job):
    db = TinyDB(str(directory / "databases" / "sources.db"))
    if len(sources) != 0:
        for entry in sources:
            db.insert({
                "name": entry[0],
                "command": entry[1],
                "loctag": entry[2],
                "selector": entry[3],
                "job": job
            })

class Server(rpyc.Service):
    def on_connect(self):
        pass

    def on_disconnect(self):
        pass

    def exposed_sh_generator(self,tag,name):
        create_source_config(tag,name)
        return sh_generator(tag,name)

    def exposed_del_job(self,job):
        return del_job(job)

    def exposed_check_cron(self,jobs):
        return check_cron(jobs)

    def exposed_add_sh_to_cron(self,name,sh,schedule):
        v = add_sh_to_cron(name,sh,schedule)
        print(v)
        return v

    def exposed_job_pauser(self,x):
        return job_pauser(x)    

if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    port = 18861
    cfg = {
        "allow_public_attrs": True,
        "allow_all_attrs": True
    }
    t = ThreadedServer(Server,port=port,protocol_config=cfg)
    print(f"Server started at :{port}")
    t.start()