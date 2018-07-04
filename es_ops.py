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
    print(obj)
    create_obj("/config/job",obj)

def get_x(r,field):
    j = r.json()
    print(j)
    o = []
    for item in j["hits"]["hits"]:
        o.append({"id": item["_id"], field: item["_source"][field]})
    return o

def get_jobs():
    r = requests.get(esurl("/config/_search"),headers={
        "Content-Type": "application/json"
    },data=json.dumps({
        "_source": True,
        "query": {
            "type": {"value": "job"}
        }
    }))
    return get_x(r,"name")

def get_sources():
    r = requests.get(esurl("/config/_search"),headers={
        "Content-Type": "application/json"
    },data=json.dumps({
        "_source": True,
        "query": {
            "type": {"value": "source"}
        }
    }))
    return get_x(r,"cmd")

def create_source(f):
    obj = {
        "cmd": f["cmd"],
        "region": f["region"]
    }
    create_obj("/config/source",obj)

def db_init():
    guarantee_index_exists("config")