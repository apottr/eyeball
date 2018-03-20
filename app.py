import sqlite3,os,csv,io
from hashlib import sha1
from pathlib import Path
from crontab import CronTab
from flask import Flask,request,render_template,redirect,Response

dbname = 'sources.db'
cron = CronTab(user=True)
directory = Path(__file__).parent.resolve() #pylint: disable=no-member
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
            """m = {
                "@hourly": "Once an hour",
                "@daily": "Once a day",
                "@weekly": "Once a week",
                "* * * * *": "Once a minute",
                "0 * * * *": "Once an hour",
                "0 0 * * *": "Once a day",
                "0 0 * * 0": "Once a week"
            }"""
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
        if len(list(cron.find_comment(job["name"]))) != 0:
            pass
        else:
            fname = (d / job["name"].replace(" ","_")).with_suffix(".sh")
            j = cron.new(command="sh {}".format(fname),comment=job["name"])
            j.setall(job["schedule"])
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

@app.route("/")
def index_route():
    return render_template("index.html",sources=get_sources(),jobs=get_jobs())

@app.route("/add_<typ>", methods=["GET","POST"])
def add_source_route(typ):
    if request.method == "GET":
        return render_template("add_{}.html".format(typ),tags=get_tags())
    else:
        f = request.form
        print(f)
        if typ == "source":
            add_source(f)
        elif typ == "job":
            x = add_job(f)
            if isinstance(x,bool) and not x: 
                return redirect("/add_job")
            x.run()
        return redirect("/")

@app.route("/del_<typ>/<name>", methods=["GET"])
def del_item_route(typ,name):
    if name:
        if typ == "job":
            delete_job(name)
        elif typ == "source":
            delete_source(name)
        return redirect("/")
    else:
        return redirect("/")

@app.route("/export_sources")
def export_sources_route():
    s = get_sources()
    h = list(s[0].keys())
    l = [";".join([item[h[0]],item[h[1]],item[h[2]]]) for item in s]
    return Response("\n".join([";".join(h)]+l),mimetype='text/csv')

@app.route("/load_sources", methods=['POST'])
def load_sources_route():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect("/")
        f = request.files['file']
        if f.filename == '':
            return redirect("/")
        fl = f.read()
        print(fl)
        csvr = csv.reader(fl.decode("utf-8").split("\n"),delimiter=";")
        sources_from_csv(csvr)
        return redirect("/")
    

if __name__ == "__main__":
    init_db()
    check_cron()
    app.run(host="0.0.0.0",debug=True)
