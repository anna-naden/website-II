# 11/9/20

import random

def proj():
    nd=48
    nr=48
    
    #NC
    r=random.random()
    if r > .65:
        nd +=1
    else:
        nr +=1

    #Alaska
    r=random.random()
    if r > .95:
        nd += 1
    else:
        nr += 1

    #Georgia 1
    r=random.random()
    if r > .5:
        nd += 1
    else:
        nr += 1
    
    #Greogia 2
    r=random.random()
    if r > .5:
        nd += 1
    else:
        nr += 1

    assert(nd+nr==100)
    return nd

random.seed(0)
nd=0
nr=0
for i in range(100000):
    d = proj()
    if d>=50:
        nd += 1
    else:
        nr += 1
print(f'd: {nd} r: {nr}')