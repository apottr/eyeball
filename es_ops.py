from kube_ops import create_cronjob,delete_cronjob
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
    srcs = f["sources"].split(",")
    name = f["name"]
    obj = {
        "name": name,
        "sources": srcs
    }
    print(obj)
    for sid in srcs:
        a = get_source(sid)
        a["id"] = sid
        print(a)
        create_cronjob(a)

    create_obj("/jobs/job",obj)
def get_x(r,field):
    j = r.json()
    o = []
    for item in j["hits"]["hits"]:
        obj = {"id": item["_id"]}
        if isinstance(field,list):
            for fi in field:
                obj[fi] = item["_source"][fi]
        else:
            obj[field] = item["_source"][field]
        o.append(obj)
    return o

def get_y(r):
    j = r.json()
    if j["found"]:
        return j["_source"]
    else:
        return {}

def get_jobs():
    r = requests.get(esurl("/jobs/_search"),headers={
        "Content-Type": "application/json"
    })
    return get_x(r,["name","sources"])

def get_job(id):
    r = requests.get(esurl(f"/jobs/job/{id}"))
    return get_y(r)

def get_sources():
    r = requests.get(esurl("/sources/_search"),headers={
        "Content-Type": "application/json"
    })
    return get_x(r,"cmd")

def get_source(id):
    r = requests.get(esurl(f"/sources/source/{id}"))
    return get_y(r)

def get_data_for_source(id, off=0, lim=10):
    r = requests.get(esurl("/data/_search"),headers={
        "Content-Type": "application/json"
    },data=json.dumps({
        "from": off, "size": lim,
        "query": {
            "match": {
                "source_id": id
            }
        }
    }))
    j = r.json()
    return [i["_source"] for i in j["hits"]["hits"]]

def create_source(f):
    obj = {
        "cmd": f["cmd"],
        "region": f["region"],
        "schedule": f["sched"]
    }
    create_obj("/sources/source",obj)

def delete_obj(index,type,id):
    if index == "jobs":
        x = get_job(id)
        if x != {}:
            for src in x["sources"]:
                delete_cronjob(src)
    r = requests.delete(esurl(f"/{index}/{type}/{id}"))
    return r.json()

def db_init():
    for i in ["jobs","sources"]:
        guarantee_index_exists(i)