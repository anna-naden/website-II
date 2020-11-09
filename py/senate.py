import random

def proj():
    d=45
    t=1
    lean_d=2
    lean_r=3
    re=47
    i=2
    total = d+t+lean_d+lean_r+re+i
    print(total)
    if total != 100:
        exit()
    for i in range(lean_d):
        r = random.random()
        if r>.25:
            d += 1
        else:
            re += 1
    for i in range(lean_r):
        r=random.random()
        if r>.25:
            re += 1
        else:
            d += 1
    r=random.random()
    if r>.5:
        re += 1
    else:
        d += 1
    d += i
    # print(f'd: {d} r:{re}')
    return d
nd=0
nr=0
nt=0
for i in range(1000):
    d = proj()
    if d>50:
        nd += 1
    elif  d<50:
        nr += 1
    else:
        nt += 1
print(f'd: {nd} r: {nr} t: {nt}')