import re,sys,json

def parse_selector(sel):
    #sample selector
    #xml({"time": "fieldname", "text": "fieldname"})
    m = re.findall(r"(xml|json|image|html)\((.+)?\)",sel)
    return m[0]

def parse_xml(args):
    return {"time": "", "text": ""}

def parse_json(args):
    return {"time": "", "text": ""}

def parse_image(args):
    return ""

def parse_html(args):
    return {"time": "", "text": ""}

def exec_selector(sel,fname):
    with open(fname) as f:
        s = parse_selector(sel)
        d = None
        if s[0] == "xml":
            d = parse_xml(s[1])
        elif s[0] == "json":
            d = parse_json(s[1])
        elif s[0] == "image":
            d = parse_image(s[1])
        elif s[0] == "html":
            d = parse_html(s[1])
    
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
    print(exec_selector(sys.argv[1],sys.argv[2]))