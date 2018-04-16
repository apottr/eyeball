import os,csv,io
from helper_functions.helper_functions import * #pylint: disable=W0614
from helper_functions.disk_manager_functions import * #pylint: disable=W0614
from parser_functions.parser_functions import * #pylint: disable=W0614
from flask import Flask,request,render_template,redirect,Response
app = Flask(__name__)

@app.route("/")
def index_route():
    return render_template("index.html",sources=get_sources(),jobs=get_jobs())

@app.route("/manager")
def disk_manager_route():
    return render_template("disk_manager.html",devices=get_disks())

@app.route("/manager/check")
def dm_check_new_route():
    pass

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

@app.route("/models")
def models_index_route():
    d,p = get_models()
    return render_template("models.html",detectors=d,predictors=p)

if __name__ == "__main__":
    init_db()
    check_cron()
    app.run(host="0.0.0.0",debug=True)
