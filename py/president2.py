import random

def proj():
    #Georgia
    r = random.random()
    if r > .5:
        return "D"
    
    #Pennsylvania
    r = random.random()
    if r > .5:
        return "D"

    #North Carolina
    r = random.random()
    if r > .75:
        return "D"

    #Nevada
    r=random.random()
    if r > .5:
        return "D"
    #Alaska
    r = random.random()
    if r > .75:
        return "D"
    return "R"
nd=0
nr=0
nt=0
for i in range(1000):
    result = proj()
    if result == "D":
        nd += 1
    elif result == "R":
        nr += 1
    else:
        nt += 1
print(f'd: {nd} r: {nr} t: {nt}')