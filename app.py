from flask import Flask,render_template,jsonify,request,redirect
from es_ops import db_init,get_jobs,get_sources,create_job,create_source

app = Flask(__name__)

@app.route("/")
def index_route():
    return render_template("index.html",jobs=get_jobs(),sources=get_sources())

@app.route("/add_<typ>",methods=["GET","POST"])
def add_route(typ):
    if request.method == "POST":
        if typ == "job":
            create_job(request.form)
        elif typ == "source":
            create_source(request.form)
        return redirect("/")
    else:
        if typ == "job":
            return render_template("add_job.html",sources=get_sources())
        else:
            return render_template(f"add_{typ}.html")

@app.route("/get_<name>")
def get_route(name):
    if name == "sources":
        return jsonify(get_sources())
    else:
        return jsonify(get_jobs())

if __name__ == "__main__":
    db_init()
    app.run(host="0.0.0.0")