from kubernetes import client,config
import platform

config.load_kube_config()
v1 = client.CoreV1Api()

def get_servers():
    out = []
    for item in v1.list_node().items:
        for jtem in item.status.addresses:
            if jtem.type == "Hostname":
                if jtem.address != platform.node():
                    out.append(jtem.address)
    return out
if __name__ == "__main__":
    a = get_servers()
    print(a)