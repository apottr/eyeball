from flask import Flask,render_template,jsonify
from es_ops import get_jobs,get_sources,db_init

app = Flask(__name__)

@app.route("/")
def index_route():
    return render_template("index.html",jobs=get_jobs(),sources=get_sources())

@app.route("/get_<name>")
def get_route(name):
    if name == "sources":
        return jsonify(get_sources())
    else:
        return jsonify(get_jobs())

if __name__ == "__main__":
    db_init()
    app.run(host="0.0.0.0")