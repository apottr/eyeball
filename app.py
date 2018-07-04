from flask import Flask,render_template,jsonify,request,redirect
from es_ops import db_init,get_jobs,get_sources,create_job,create_source
from kube_ops import get_servers
app = Flask(__name__)

@app.route("/")
def index_route():
    return render_template("idx.htm")

@app.route("/api/get_<name>")
def get_route(name):
    if name == "sources":
        return jsonify(get_sources())
    elif name == "regions":
        return jsonify(get_servers())
    elif name == "jobs":
        return jsonify(get_jobs())

@app.errorhandler(404)
def four_oh_four(e):
    return redirect("/")

if __name__ == "__main__":
    db_init()
    app.run(host="0.0.0.0",debug=True)