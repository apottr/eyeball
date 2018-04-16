import libmount as mnt
import functools as ft
from pathlib import Path

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
        p = Path("/sys/block/{}".format(item.parent.name))
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

if __name__ == "__main__":
    #print([item.source for item in get_mounted_disks()])
    d = get_disk("/dev/sdc1")
    print(str(directory / "mounted"))
    print(mount_disk(d,str(directory / "mounted")))