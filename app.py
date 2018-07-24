from flask import Flask,render_template,jsonify,request,redirect
from es_ops import db_init,get_jobs,get_sources,create_job,create_source,delete_obj,get_data_for_source
from kube_ops import get_servers
app = Flask(__name__)

@app.route("/", defaults={'path': ''})
@app.route("/<path:path>")
def index_route(path):
    return render_template("idx.htm")

@app.route("/api/get-<name>")
def get_route(name):
    if name == "sources":
        return jsonify(get_sources())
    elif name == "regions":
        return jsonify(get_servers())
    elif name == "jobs":
        return jsonify(get_jobs())

@app.route("/api/get-<name>/<id>")
def get_det_route(name,id):
    if name == "source":
        return jsonify(get_data_for_source(id))

@app.route("/api/add-<name>",methods=["POST"])
def add_route(name):
    if name == "source":
        create_source(request.form)
    elif name == "job":
        create_job(request.form)

    return jsonify({"status": f"created {name} successfully"})

@app.route("/api/del-<name>",methods=["POST"])
def del_route(name):
    id = request.form["id"]
    delete_obj(f"{name}s",name,id)
    return jsonify({"status": f"deleted {id} sucessfully"})

if __name__ == "__main__":
    db_init()
    app.run(host="0.0.0.0",debug=True)