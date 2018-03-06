import sqlite3,os
from hashlib import sha1
from pathlib import Path

from crontab import CronTab

conn = sqlite3.connect('sources.db')
cron = CronTab(user=True)
directory = Path(__file__).parent

def add_source(src):
    c = conn.cursor()
    try:
        c.execute('insert into sources values (?,?,?)',(src["name"],src["command"],src["loctag"]))
        return True
    except sqlite3.DatabaseError as e:
        print(e)
        return False

def lookup_by_tag(tag):
    c = conn.cursor()
    c.execute('select * from sources where loctag like "%?%"',(tag,))
    return c.fetchall()

def sh_generator(tag):
    lines = ["#!/bin/sh"]
    f = lookup_by_tag(tag)
    if len(f) != 0:
        for entry in f:
            lines.append("{} #{}".format(entry[1],entry[0]))
    return lines

def add_sh_to_cron(name,sh,schedule):
    out = "\n\n".join(sh)
    d = directory / "shell_files"
    fname = (d / name).with_suffix(".sh")
    f = open(fname)
    f.write(out)
    j = cron.new(command="sh {}".format(fname),comment=name)
    j.setall(schedule)
    v = j.is_valid()
    if v:
        return True
    else:
        os.remove(fname)
        return False