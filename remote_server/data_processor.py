import nltk,sqlite3,sys,time
from pathlib import Path
from nltk.corpus import stopwords as sw
from sel_module import exec_selector
from tinydb import TinyDB, Query

directory = Path(__file__).parent.resolve() #pylint: disable=no-member
xdb= TinyDB(str(directory / "databases" / "sources.db"))

stopwords = None

def get_sources():
    return [item for item in xdb]

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
    d = xdb.search(Query().name == name)[0]
    return d["selector"]

def pruning(string):
    remap = {
        "&lt;": "",
        "&gt;": ""
    }
    s = string.translate(remap)
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

def process_text(sentence):
    tokens = nltk.sent_tokenize(sentence)
    tokens = [nltk.word_tokenize(sent) for sent in tokens]
    tok = []
    for sent in tokens:
        out = sent
        """sw_chunk = {"stopword": "", "words": []}
        for word in sent:
            if word not in stopwords:
                sw_chunk["words"].append(word)
            else:
                out.append(sw_chunk)
                sw_chunk = {"stopword": word, "words": []}"""
        tok.append(out)

    return {"entities": tok}

def process_text_old(sentence):
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
                    d.append(process_text(txt)["entities"])
            elif "data" in data:
                for item in data["data"]:
                    d.append(item)
            fin["times"] = data["time"]
            fin["entites"] = d
            fin["filename"] = f.stem
            db.insert(fin)
            print("finished {}".format(str(f)))
            time.sleep(0.1)
    

if __name__ == "__main__":
    #nltk_setup(["punkt","averaged_perceptron_tagger","maxent_ne_chunker","words"])
    nltk_setup(["punkt","words","stopwords"])
    #stopwords = set(sw.words("english"))
    for source in get_sources():
        #if check_if_source_is_used(source["name"]):
        handle_source(source["name"])
    