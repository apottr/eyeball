import zipfile,requests,sqlite3,csv,os
from io import BytesIO
from pathlib import Path
from shapely.geometry import shape
from shapely.wkt import dumps as wkt_dumps
from json import loads
import pandas as pd

directory = Path(__file__).parent.resolve() #pylint: disable=no-member

dbname = (directory / "lookups.db")

files_dir = (directory / "lookup_temp")

def check_if_exists():
    conn = sqlite3.connect(str(dbname))
    c = conn.cursor()
    out = [False,False]
    try:
        c.execute("select * from geonames_countries limit 1")
        out[0] = True
        c.execute("select * from geonames_shapes limit 1")
        out[1] = True
    except:
        pass
    return out

def download_and_unzip(url,fname):
    files_dir.mkdir(exist_ok=True)
    r = requests.get(url)
    with zipfile.ZipFile(BytesIO(r.content)) as zf:
        zf.extract(fname,path=str(files_dir))

def to_csv(fname,cursor,table):
    with open(str(files_dir / fname)) as f:
        r = csv.reader(f,delimiter='\t')
        chunk = []
        for line in r:
            if len(chunk) == 100000:
                print(chunk[0])
                q = "insert into {} values ({})".format(table,",".join(["?" for i in range(len(chunk[0]))]))
                print(q)
                cursor.executemany(q,chunk)
                chunk = []
            chunk.append(tuple(line))
        

def pull_allCountries():
    url = "http://download.geonames.org/export/dump/allCountries.zip"
    fname = "allCountries.txt"
    conn = sqlite3.connect(str(dbname))
    c = conn.cursor()
    print("downloading allCountries")
    if not (files_dir / fname).is_file():
        download_and_unzip(url,fname)
    print("finished downloading and unzipping allCountries")
    c.execute("""create table geonames_countries (geonameid text, name text, asciiname text, 
    alternatenames text, latitude text, longitude text, feature_class text, feature_code text, country_code text, 
    cc2 text, admin1_code text, admin2_code text, admin3_code text, admin4_code text, population number,
     elevation number, dem text, timezone text, modification_date text)""")
    to_csv(fname,c,"geonames_countries")
    conn.commit()
    conn.close()
    os.remove(str(files_dir / fname))
    

def pull_shapes_all_low():
    url = "http://download.geonames.org/export/dump/shapes_all_low.zip"
    fname = "shapes_all_low.txt"
    conn = sqlite3.connect(str(dbname))
    print("downloading shapes_all_low")
    download_and_unzip(url,fname)
    print("finished downloading and unzipping shapes_all_low")
    df = pd.read_table(str(files_dir / fname),names=["geonameid","geojson"],skiprows=1)
    df['geojson'] = df['geojson'].apply(lambda x: shape(loads(x)).wkt)
    df.columns = ['geonameid','wkt']
    df.to_sql("geonames_shapes",conn,chunksize=10000)
    conn.close()
    os.remove(str(files_dir / fname))

if __name__ == "__main__":
    d = check_if_exists()
    if not d[0]:
        pull_allCountries()
    if not d[1]:
        pull_shapes_all_low()