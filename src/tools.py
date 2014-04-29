__author__ = 'juliewe'

import json

filepath="myfile.json"

dataset=[['bird','animal',1],['bird','device',0]]

with open(filepath,'w') as outpath:
    json.dump(dataset,outpath)

with open(filepath,'r') as inpath:
    inputdata=json.load(inpath)

print inputdata
