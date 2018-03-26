import re,sys,json
from xml.dom.minidom import parseString
from bs4 import BeautifulSoup
def parse_selector(sel):
    #sample selector
    #xml({"time": "fieldname", "text": "fieldname"})
    m = re.findall(r"(xml|json|image|html)\((.+)?\)",sel)
    return m[0]

def generic_handler(args,data,howtoget,pruner):
    obj = {}
    for key in args.keys():
        if isinstance(args[key],list):
            d = []
            for tag in args[key]:
                d += [pruner(item) for item in howtoget(data,tag)]
        else if args[key] != "$FILENAME":
            d = [pruner(item) for item in howtoget(data,args[key])]
        else:
            d = "$REPLACE_WITH_FILENAME"
        obj[key] = d
    return obj

def parse_xml(args,data):
    howtoget = lambda x,y: x.getElementsByTagName(y)
    pruner = lambda x: x.firstChild.toxml()
    return generic_handler(args,parseString(data),howtoget,pruner)

def howtoget_json(data,tag):
    out = []
    for key in data.keys():
        if isinstance(data[key],list):
            d = []
            for item in data[key]:
                x = howtoget_json(item,tag)
                if x != []:
                    d.append(x)
            out += d
    if tag in data:
        out.append(data[tag])
    return out

def parse_json(args,data):
    howtoget = howtoget_json
    pruner = lambda x: x

    return generic_handler(args,json.loads(data),howtoget,pruner)

def parse_image(args,data):
    return ""

def parse_html(args,data):
    howtoget = lambda x,y: x.select(y)
    pruner = lambda x: x.get_text()
    return generic_handler(args,BeautifulSoup(data),howtoget,pruner)

def exec_selector(sel,fname):
    print(sel,fname)
    with open(fname) as f:
        s = parse_selector(sel)
        d = None
        data = "\n".join(f.readlines())
        args = json.loads(s[1])
        if s[0] == "xml":
            d = parse_xml(args,data)
        elif s[0] == "json":
            d = parse_json(args,data)
        elif s[0] == "image":
            d = parse_image(args,data)
        elif s[0] == "html":
            d = parse_html(args,data)
        for key in d.keys():
            if d[key] == "$REPLACE_WITH_FILENAME":
                d[key] = fname
        return d

if __name__ == "__main__":
    """sels = [
        'xml({"time": "fieldname", "text": "fieldname"})',
        'json({"time": "fieldname", "text": "fieldname"})',
        'image()',
        'html({"time": "css_selector", "text": "css_selector"})'
    ]
    for selector in sels:
        print(parse_selector(selector))"""

    print(exec_selector('xml({"text": ["title","description"], "time": "date"})',"processor_test.xml"))
    print(exec_selector('json({"text": "text", "time": "time"})',"processor_test.json"))
    #print(exec_selector('html({"text": ""})'))