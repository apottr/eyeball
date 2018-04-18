import os,csv,io
from helper_functions.helper_functions import * #pylint: disable=W0614
from helper_functions.disk_manager_functions import * #pylint: disable=W0614
from parser_functions.parser_functions import * #pylint: disable=W0614
from flask import Flask,request,render_template,redirect,Response,jsonify
app = Flask(__name__)

@app.route("/")
def index_route():
    return render_template("index.html",sources=get_sources(),jobs=get_jobs(),projects=get_projects())

@app.route("/manager")
def disk_manager_route():
    return render_template("disk_manager.html",devices=get_disks())

@app.route("/manager/check")
def dm_check_new_route():
    return jsonify(get_disks())

@app.route("/add_<typ>", methods=["GET","POST"])
def add_source_route(typ):
    if request.method == "GET":
        jbs = get_jobs()
        return render_template("add_{}.html".format(typ),tags=get_tags(),jobs=jbs)
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
        elif typ == "project":
            add_project(f)

        return redirect("/")

@app.route("/del_<typ>/<name>", methods=["GET"])
def del_item_route(typ,name):
    if name:
        if typ == "job":
            delete_job(name)
        elif typ == "source":
            delete_source(name)
        elif typ == "project":
            delete_project(name)
        return redirect("/")
    else:
        return redirect("/")

@app.route("/pause_job/<name>", methods=["GET"])
def pause_job_route(name):
    if name:
        for job in cron.find_comment(name):
            if job.is_enabled():
                job.enable(False)
            else:
                job.enable()
        cron.write()
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
    
@app.route("/search", methods=['GET','POST'])
def search_route():
    if request.method == 'POST':
        data = perform_search(request.form)
        return render_template("search_done.html",data=data)
    else:
        return render_template("search_start.html")

@app.route("/project/<projname>")
def project_main_route(projname):
    if projname != None:
        print(projname)
        src = get_sources_for_project(projname)
        print(src)
        dbs = get_datasets_for_project(projname)
        rls = get_rules_for_project(projname)
        #src,dbs,rls = [{"name": "test job", "schedule": "* * * * *"}],[{"name": "MA_PCLS_2018.shp", "type": "shapefile"}],[{"name": "match move","data": "\w{0,4} (departs|enters|leaves|arrives) \w{0,4}"}] 
        return render_template("project_home.html",name=projname,sources=src,datasets=dbs,rules=rls)
    else:
        return redirect("/")

@app.route("/project/<projname>/dashboard")
def project_dash_route(projname):
    return render_template("project_dashboard.html")

@app.route("/project/<projname>/add_<typ>",methods=["GET","POST"])
def project_add_source_route(projname,typ):
    if request.method == "GET":
        jbs = []
        pjbs = [item["job.name"] for item in get_sources_for_project(projname)]
        for item in [item["name"] for item in get_jobs()]:
            if item in pjbs:
                jbs.append({"name": item, "checked": True})
            else:
                jbs.append({"name": item, "checked": False})
        return render_template("padd_{}.html".format(typ),jobs=jbs)
    else:
        set_sources_for_project(projname,request.form.getlist("jobs"))
        return redirect("/project/{}".format(projname))

if __name__ == "__main__":
    init_db()
    check_cron()
    app.run(host="0.0.0.0",debug=True)
