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
        c.execute('create table jobs (name text, tags text, schedule text)')

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
    try:
        c.execute('insert into jobs values (?,?,?)',(src["name"],src["tags"],src["schedule"]))
        conn.commit()
        conn.close()
    except Exception as e:
        print(e)
    add_sh_to_cron(src["name"],sh,src["schedule"])
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
            m = {
                "@hourly": "Once an hour",
                "@daily": "Once a day",
                "@weekly": "Once a week",
                "* * * * *": "Once a minute",
                "0 * * * *": "Once an hour",
                "0 0 * * *": "Once a day",
                "0 0 * * 0": "Once a week"
            }
            out.append({
                "name": item[0],
                "tags": item[1],
                "schedule": m[item[2]]
            })
    return out

def sh_generator(tag,name):
    lines = []
    f = lookup_by_tag(tag)
    if len(f) != 0:
        for entry in f:
            d = (directory / "data" / name / entry[0])
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
        return True
    else:
        os.remove(fname)
        return False

def delete_job(name):
        try:
            os.remove("shell_files/{}.sh".format(name))
        except Exception as e:
            print(e)
        cron.remove_all(comment=name)
        d = (directory / "data" / name)
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

def delete_source(name):
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    c.execute('delete from sources where name=?',(name,))
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
        a[href^="/del_"] {
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
def del_job_route(name):
    if name:
        delete_job(name)
        return redirect("/")
    else:
        return redirect("/")
@app.route("/del_source/<name>", methods=["GET"])
def del_source_route(name):
    if name:
        delete_source(name)
        return redirect("/")
    else:
        return redirect("/")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
