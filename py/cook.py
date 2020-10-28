import pandas as pd
import numpy as np
import random
import tabula
from tabula import read_pdf
# import tabula
from tabulate import tabulate

def proj(nvotes, verbose=False):
    model = [1, .9,.75,.6, .5, .4, .25, .1, 0.]
    nblue = 0
    for vote in nvotes:
        r = random.random()
        cat = vote[0]+1
        if r<model[cat]:
            nblue += vote[1]
            if verbose:
                print(f'blue {r} {model[cat]}')
        else:
            if verbose:
                print("red")   
    return nblue

df = read_pdf('election/cook.pdf', pages=1)[1]
solidb = df['SOLID DEMOCRAT'][3:]
likelyb = df['LIKELY DEMOCRAT'][3:]
leanb = df['LEAN DEMOCRAT'][3:]
tossup = df['TOSS UP'][3:]
leanr = df['LEAN REPUBLICAN'][3:]
likelyr = df['LIKELY REPUBLICAN'][3:]
solidr = df['SOLID REPUBLICAN'][3:]

simulate = False
sum=0
j=0
nvotes = []
nblocks = 0
for cat in [solidb, likelyb, leanb, tossup, leanr, likelyr, solidr]:
    for i in range(3,19):
        s=cat[i]
        if type(s) != type(1.0):
            nblocks += 1
            beg = s.find('(')
            end = s.find(')')
            n=int(s[beg+1:end])
            sum += n
            if simulate:
                nvotes.append([3,10])
            else:
                nvotes.append([j,n])
            # print(j,s,n)
    j += 1

#There are a total of 538 electoral votes
print(sum)
if not simulate and (sum != 538):
    exit()

random.seed(0)
nruns = 1000
sum=0
nblue = 0
nred = 0
ntie = 0
threshold = 269
if simulate:
    threshold = 560/2
for i in range(nruns):
    pr = proj(nvotes)
    if pr==threshold:
        ntie += 1
    elif pr<threshold:
        nred +=1
    else:
        nblue += 1
    sum += pr
#311.417 0.5788420074349442 (1000 runs)
print(sum/nruns, sum/(nruns*538))
print(nblocks)
print(f'blue {nblue} red {nred} tie {ntie}')