from kubernetes import client,config
import platform

config.load_kube_config()
v1 = client.CoreV1Api()
bb1 = client.BatchV1beta1Api()

def get_servers():
    out = []
    for item in v1.list_node().items:
        for jtem in item.status.addresses:
            if jtem.type == "Hostname":
                if jtem.address != platform.node():
                    out.append(jtem.address)
    return out

def create_cronjob(cfg):
    cronjob = client.V1beta1CronJob(
        metadata=client.V1ObjectMeta(
            name=cfg["id"].lower()+"-cronjob"
        ),
        spec=client.V1beta1CronJobSpec(
            schedule=cfg["schedule"],
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
                                            value=cfg["id"]
                                        )
                                    ],
                                )
                            ],
                            restart_policy="OnFailure",
                            node_name=cfg["region"]
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
    id = "GDTLqWQBMu4OXDrF1OBa"
    #create_cronjob(id)
    delete_cronjob(id)