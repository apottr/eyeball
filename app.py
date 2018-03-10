import sqlite3,os
from hashlib import sha1
from pathlib import Path
from crontab import CronTab
from flask import Flask,request,render_template,redirect

dbname = 'sources.db'
cron = CronTab(user=True)
directory = Path(__file__).parent.resolve()
app = Flask(__name__)

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
        c.execute('create table jobs (name text, tags text)')

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
    sh = sh_generator(src["tags"])
    try:
        c.execute('insert into jobs values (?,?)',(src["name"],src["tags"]))
        conn.commit()
        conn.close()
    except Exception as e:
        print(e)
    add_sh_to_cron(src["name"],sh,"")
    #cron.write()
    print(cron)

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
                "tags": item[1]
            })
    return out

def sh_generator(tag):
    lines = []
    f = lookup_by_tag(tag)
    if len(f) != 0:
        for entry in f:
            lines.append("{} #{}".format(entry[1],entry[0]))
    return lines

def add_sh_to_cron(name,sh,schedule):
    out = "\n\n".join(["#!/bin/sh",*sh])
    d = directory / "shell_files"
    fname = (d / name).with_suffix(".sh")
    f = open(fname,"w+")
    f.write(out)
    j = cron.new(command="sh {}".format(fname),comment=name)
    j.setall(schedule)
    v = j.is_valid()
    #v = True
    if v:
        return True
    else:
        os.remove(fname)
        return False

def delete_job(name):
        os.remove("shell_files/{}.sh".format(name))
        cron.remove_all(comment=name)
        conn = sqlite3.connect(dbname)
        c = conn.cursor()
        c.execute('delete from jobs where name=?',(name,))
        conn.commit()
        conn.close()

@app.route("/")
def index_route():
    return render_template("index.html",sources=get_sources(),jobs=get_jobs())

@app.route("/css")
def css_route():
    return """
        input[name="command"], .snippet{
            font-family: monospace;
        }
        ul {
            list-style-type: none;
        }
        a[href^="/del_job/"] {
            color: #f00;
        }
    """

@app.route("/add_source", methods=["GET","POST"])
def add_source_route():
    if request.method == "GET":
        return render_template("add_source.html",tags=get_tags())
    else:
        f = request.form
        print(f)
        add_source(f)
        return redirect("/")

@app.route("/add_job", methods=["GET","POST"])
def add_job_route():
    if request.method == "GET":
        return render_template("add_job.html",tags=get_tags())
    else:
        f = request.form
        print(f)
        add_job(f)
        return redirect("/")

@app.route("/del_job/<name>", methods=["GET"])
def del_job_method(name):
    if name:
        delete_job(name)
        return redirect("/")
    else:
        return redirect("/")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
