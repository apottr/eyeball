import platform
if platform.system() == "Darwin":
    #from .darwin_mount_handler import mnt
    pass
else:
    import libmount as mnt #pylint: disable=E0401
import functools as ft
from pathlib import Path
import subprocess

directory = Path(__file__).parent.parent.resolve() #pylint:disable=no-member

def get_mounted_disks():
    tb = mnt.Table("/proc/self/mountinfo")
    out = []
    for fs in iter(ft.partial(tb.next_fs),None):
        if "/dev/s" in fs.source:
            out.append(fs)
    return out

def get_all_disks():
    p = Path("/sys/block")
    return list(p.glob("*/device"))

def get_all_logical_disks():
    d = get_all_disks()
    out = []
    for item in d:
        p = Path(f"/sys/block/{item.parent.name}")
        for pd in p.glob("*/start"):
            out.append({"device": item.parent.name, "partition": pd.parent.name})
    return out

def get_disks():
    m = [item.source for item in get_mounted_disks()]
    out = []
    for disk in get_all_logical_disks():
        d = "/dev/{}".format(disk["partition"])
        out.append({
            "device": d,
            "mounted": (True if d in m else False)
        })
    return out

def mount_disk(dobj,target):
    if dobj["mounted"]:
        return False
    ctx = mnt.Context()
    ctx.target = target
    ctx.source = dobj["device"]
    try:
        ctx.mount()
    except Exception as e:
        print(e)
        return False
    return True

def get_disk(target):
    for disk in get_disks():
        if disk["device"] == target:
            return disk

def get_size_of_path(p):
    s = subprocess.Popen(f"du -sh {str(p)}",shell=True,stdout=subprocess.PIPE)
    d = s.stdout.readline().decode("ascii").strip().split("\t")
    return {
        "size": d[0],
        "folder": Path(d[1]).name
    }

def get_total_data_size():
    p = directory / "data"
    return get_size_of_path(p)

def get_job_data_size():
    p = (directory / "data").glob("*/")
    out = []
    for d in p:
        if d.is_dir():
            out.append(get_size_of_path(d))
    return out

    

if __name__ == "__main__":
    #print([item.source for item in get_mounted_disks()])
    #d = get_disk("/dev/sdc1")
    #print(str(directory / "mounted"))
    #print(mount_disk(d,str(directory / "mounted")))
    print(get_total_data_size())
    print(get_job_data_size())