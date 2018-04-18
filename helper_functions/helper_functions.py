import sqlite3,os
from pathlib import Path
from .source_functions import * #pylint:disable=W0614
from .project_functions import * #pylint:disable=W0614
from .globals import directory,dbname

def init_db():
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    try:
        c.execute('select * from sources')
    except sqlite3.OperationalError:
        c.execute('create table sources (name text, command text, loctag text, selector text)')
    try:
        c.execute('select * from jobs')
    except sqlite3.OperationalError:
        c.execute('create table jobs (name text, tags text, schedule text, wkt string)')
    try:
        c.execute("select * from projects")
    except sqlite3.OperationalError:
        c.execute('create table projects (name text, sources text, datasets text, rules text)')
    c.close()

def get_models():
    return None,None