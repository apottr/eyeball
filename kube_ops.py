from kubernetes import client,config
import platform

config.load_kube_config()
v1 = client.CoreV1Api()
bb1 = client.BatchV1beta1Api()
def get_servers():
    out = []
    for item in v1.list_namespaced_pod("default").items:
        n = item.metadata.name
        if n.split(".")[0] == "eyeball":
            out.append(item.metadata.name)
    return out
if __name__ == "__main__":
    a = get_servers()
    print(a)

def create_cronjob(cfg):
    cronjob = client.V1beta1CronJob(
        metadata=client.V1ObjectMeta(
            name=cfg["_id"].lower()+"-cronjob"
        ),
        spec=client.V1beta1CronJobSpec(
            schedule=cfg["_source"]["schedule"],
            job_template=client.V1beta1JobTemplateSpec(
                spec=client.V1JobSpec(
                    template=client.V1PodTemplateSpec(
                        spec=client.V1PodSpec(
                            containers=[
                                client.V1Container(
                                    name="eyeball-remote-cron",
                                    image="eyeball-remote-cron:v1",
                                    env=[
                                        client.V1EnvVar(
                                            name="ID",
                                            value=cfg["_id"]
                                        )
                                    ],
                                )
                            ],
                            restart_policy="OnFailure",
                            node_name="bluesteel"
                        )
                    )
                )
            )
        ))
    bb1.create_namespaced_cron_job("default",cronjob)

def delete_cronjob(id):
    bb1.delete_namespaced_cron_job(
        id.lower()+"-cronjob",
        "default",
        client.V1DeleteOptions())

if __name__ == "__main__":
    obj = {
        "_index":"sources",
        "_type":"source",
        "_id":"GDTLqWQBMu4OXDrF1OBa",
        "_score":1.0,
        "_source":{
            "cmd": "curl -I youtube.com", 
            "region": "bluesteel", 
            "schedule": "* * * * *"
        }
    }
    '''create_cronjob(obj)'''
    delete_cronjob(obj["_id"])