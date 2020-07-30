import csv
import json


def csvread(fname, bids_demogr=False, id=None):
    res = []
    if bids_demogr:
        with open(fname, 'r') as fr:
            lines_r = csv.reader(fr)
            for row in lines_r:
                res.append(row[0].split(id))

    else:
        with open(fname, 'r') as fr:
            lines_r = csv.reader(fr)
            for row in lines_r:
                res.append(row)
    return res




def csvappendaline(fname, l_str):
    with open(fname, 'a') as fw:
        f_w = csv.writer(fw, lineterminator="\n")
        f_w.writerow(l_str)





def csvappendlines(fname, l_str):
    with open(fname, 'a') as fw:
        f_w = csv.writer(fw, lineterminator="\n")
        f_w.writerows(l_str)








def jsonupdate(f, ele):
    with open(f, 'r+') as jf:
        jdict = json.load(jf)
        jdict.update(ele)
        jf.seek(0)
        json.dump(jdict, jf, sort_keys=True, indent=8)





def jsonread(f):
    with open(f, 'r') as jf:
        jdict = json.load(jf)
    return jdict
