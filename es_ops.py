import requests,os,json

if "ES_SERVICE_SERVICE_HOST" in os.environ:
    ESHOST = os.environ["ES_SERVICE_SERVICE_HOST"]
    ESPORT = os.environ["ES_SERVICE_SERVICE_PORT"]
    es = f"{ESHOST}:{ESPORT}"
else:
    es = "localhost:8001/api/v1/namespaces/default/services/es-service/proxy"

esurl = lambda x: f"http://{es}{x}"

def guarantee_index_exists(idx):
    r = requests.get(esurl(f"/{idx}"))
    d = r.json()
    if "error" in d:
        requests.put(esurl(f"/{idx}"))

def create_obj(p,obj):
    r = requests.post(esurl(p),data=json.dumps(obj),headers={"Content-Type":"application/json"})
    print(r.json())
    return r

def create_job(f):
    obj = {
        "name": f["name"],
        "sources": f.getlist("sources")
    }
    create_obj("/jobs/job",obj)

def get_jobs():
    r = requests.get(esurl("/jobs/_search"))
    return r.json()

def get_sources():
    r = requests.get(esurl("/sources/_search"))
    j = r.json()
    o = []
    for item in j["hits"]["hits"]:
        o.append({"id": item["_id"], "cmd": item["_source"]["cmd"]})
    return o

def create_source(f):
    obj = {
        "cmd": f["cmd"]
    }
    create_obj("/sources/source",obj)

def db_init():
    for idx in ["jobs","sources"]:
        guarantee_index_exists(idx)