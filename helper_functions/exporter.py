from subprocess import Popen
from .globals import directory

exports_dir = directory / "exports"

def create_archive(fname):
    fn = str(exports_dir / fname)
    d = Popen(f"tar -czf {fn} databases; tar -rf {fn} data",shell=True)
    return d
    
def archive_filename(fname):
    return str(exports_dir / fname)