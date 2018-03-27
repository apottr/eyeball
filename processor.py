import nltk,sqlite3,sys,time
from pathlib import Path
from sel_module import exec_selector
from helper_functions import get_sources,check_if_source_is_used
from tinydb import TinyDB, Query

directory = Path(__file__).parent.resolve() #pylint: disable=no-member
dbname= str(directory / "sources.db")


def nltk_setup(depends):
    d = directory / "nltk_data_storage"

    for item in depends:
        nltk.download(info_or_id=item,download_dir=str(directory / "nltk_data_storage"))
    nltk.data.path.append(str(directory / "nltk_data_storage"))
    gi = d / ".gitignore"
    if not gi.is_file():
        gi.touch()
        with gi.open("r+") as f:
            f.write("*\n*/\n!.gitignore")

def get_source_selector(name):
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    c.execute("select selector from sources where name=?",(name,))
    r = c.fetchall()
    c.close()
    return r[0][0]

def pruning(string):
    s = string.replace("&lt;","")
    s = s.replace("&gt;","")
    s = s.replace(", "," ")
    s = s.split("—")[1]
    return s

def reassemble(tree):
    out = []
    for leaf in tree:
        if hasattr(leaf,"label"):
            out.append(leaf)
        else:
            out.append(leaf[0])
    return out

def recurse_reassemble(tree):
    out = []
    for leaf in tree:
        if hasattr(leaf,"label") and leaf.label() == "S":
            out += recurse_reassemble(leaf)

def pull_ner(sentence):
    sente = sentence
    tokens = nltk.sent_tokenize(sente)
    tokens = [nltk.word_tokenize(sent) for sent in tokens]
    tokens = [nltk.pos_tag(sent) for sent in tokens]
    tree = [nltk.ne_chunk(token,binary=True) for token in tokens]
    data = []
    for item in tree:
        data += reassemble(item)
    items = []
    for i in range(len(data)):
        item = data[i]
        if hasattr(item,"label"):
            items.append({
                "idx": i,
                "obj": item.leaves(),
                "before": data[i-1] if i > 1 else "",
                "after": data[i+1] if i < len(data)-1 else ""
            })
    return {
        "filename": "",
        "entities": items
    }

def handle_source(name):
    sel = get_source_selector(name)
    folders = (directory / "data").glob("*/{}".format(name))
    for folder in folders:
        db = TinyDB(folder / "db.json")
        files = list(folder.glob("*"))
        for f in files:
            if f.stem == "db":
                continue
            if len(db.search(Query().filename == f.stem)) != 0:
                continue
            print("doing {}".format(str(f)))
            fin = {}
            data = exec_selector(sel,f)
            d = []
            if "text" in data:
                for txt in data["text"]:
                    d.append(pull_ner(txt)["entities"])
            fin["times"] = data["time"]
            fin["entites"] = d
            fin["filename"] = f.stem
            db.insert(fin)
            print("finished {}".format(str(f)))
            time.sleep(1)
    

if __name__ == "__main__":
    nltk_setup(["punkt","averaged_perceptron_tagger","maxent_ne_chunker","words"])
    for source in get_sources():
        if check_if_source_is_used(source["name"]):
            handle_source(source["name"])
    