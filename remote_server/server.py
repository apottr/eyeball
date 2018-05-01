#pylint: skip-file
import rpyc
from crontab import CronTab

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

class Server(rpyc.Service):
    def on_connect(self):
        pass

    def on_disconnect(self):
        pass

    def exposed_add_job(self):
        pass

if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(Server,port=18861)
    t.start()