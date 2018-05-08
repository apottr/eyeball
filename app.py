import os,csv,io,time
from helper_functions.helper_functions import * #pylint: disable=W0614
from helper_functions.disk_manager_functions import * #pylint: disable=W0614
from helper_functions.remote_node_functions import * #pylint: disable=W0614
from helper_functions.exporter import * #pylint: disable=W0614
from parser_functions.parser_functions import * #pylint: disable=W0614
from flask import Flask,request,render_template,redirect,Response,jsonify,session,send_file
app = Flask(__name__)

app.secret_key = "aaaaaaaaaabbbbbbbbbbccccccccddddddeeeeeefffffggggggg1111"
@app.route("/")
def index_route():
    return render_template("index.html",sources=get_sources(),jobs=get_jobs(),projects=get_projects(),nodes=get_nodes())

@app.route("/diag")
def diag_panel_route():
    return render_template("diag.html",total_size=get_total_data_size(),job_size=get_job_data_size())

@app.route("/diag/pause_<x>")
def diag_pause_route(x):
    if x:
        job_pauser(x,"localhost")
    return redirect("/diag")

@app.route("/diag/download")
def diag_download_route():
    fn = "archive_{}.tar.gz".format(time.gmtime())
    d = create_archive(fn)
    session["fname"] = fn
    session["sp"] = d
    return redirect("/diag")

@app.route("/diag/download/poll")
def diag_download_poll_route():
    if "sp" in session:
        return jsonify({"status": session["sp"].poll()})
    else:
        return jsonify({"status": None})

@app.route("/diag/download/final")
def diag_download_final_route():
    return send_file(archive_filename(session["fname"]))

@app.route("/add_<typ>", methods=["GET","POST"])
def add_source_route(typ):
    if request.method == "GET":
        jbs = get_jobs()
        return render_template(f"add_{typ}.html",tags=get_tags(),jobs=jbs)
    else:
        f = request.form
        print(f)
        if typ == "source":
            add_source(f)
        elif typ == "job":
            x = add_job(f,"localhost")
            if isinstance(x,bool) and not x: 
                return redirect("/add_job")
            x.run()
        elif typ == "project":
            add_project(f)
        elif typ == "host":
            add_node(f)
        return redirect("/")

@app.route("/del_<typ>/<name>", methods=["GET"])
def del_item_route(typ,name):
    if name:
        if typ == "job":
            delete_job(name,"localhost")
        elif typ == "source":
            delete_source(name)
        elif typ == "project":
            delete_project(name)
        elif typ == "host":
            delete_node(name)
    
    return redirect("/")

@app.route("/pause_job/<name>", methods=["GET"])
def pause_job_route(name):
    if name:
        job_pauser(name,"localhost")
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
        src = get_sources_for_project(projname)
        dbs = get_datasets_for_project(projname)
        rls = get_rules_for_project(projname)
        #src,dbs,rls = [{"name": "test job", "schedule": "* * * * *"}],[{"name": "MA_PCLS_2018.shp", "type": "shapefile"}],[{"name": "match move","data": "\w{0,4} (departs|enters|leaves|arrives) \w{0,4}"}] 
        return render_template("project_home.html",name=projname,sources=src,datasets=dbs,rules=rls)
    else:
        return redirect("/")

@app.route("/project/<projname>/dashboard")
def project_dash_route(projname):
    pg = request.args.get("pg")
    pgidx = pg if pg else 0
    d = get_data_from_project(projname,pgidx)
    return render_template("project_dashboard.html",data=d,pgidx=pgidx)

@app.route("/project/<projname>/add_<typ>",methods=["GET","POST"])
def project_add_route(projname,typ):
    if request.method == "GET":
        jbs,alft = [],[]
        if typ == "source_job":
            jbs = get_jobs_for_project(projname,get_jobs())
        elif typ == "dataset":
            alft = ["shapefile","csv","sql","tsv"]
        return render_template(f"padd_{typ}.html",jobs=jbs,allowed_filetypes=alft)
    else:
        if typ == "source_job":
            set_sources_for_project(projname,request.form.getlist("jobs"))
        elif typ == "dataset":
            pass
        elif typ == "rule":
            add_rule_to_project(projname,request.form)
        return redirect(f"/project/{projname}")

@app.route("/project/<projname>/del_<typ>_<name>",methods=["GET"])
def project_del_route(projname,typ,name):
    if projname != None:
        if typ == "rule":
            delete_rule_from_project(projname,name)
        elif typ == "dataset":
            delete_dataset_from_project(projname,name)
    return redirect(f"/project/{projname}")

if __name__ == "__main__":
    init_db()
    remotes_check_cron()
    app.run(host="0.0.0.0",debug=True)
