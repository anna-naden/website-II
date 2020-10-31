import pandas as pd
import numpy as np
import re
import random

import PyPDF2

#Presidential
def parse_pdf(c):
    c=c.replace('\n','')
    i=0
    cats = []

    regexpr = r'Electoral Votes'
    outer = re.compile(regexpr)
    regexpr = r'\(\d+\)'
    inner = re.compile(regexpr)
    
    matches = outer.finditer(c)
    for m in matches:
        start, end = m.span()
        cats.append(start)
    assert(len(cats) == 7)
    cats.append(len(c))
    
    cat_lines=[]
    for i in range(7):
        cat_line = c[cats[i]:cats[i+1]]
        cat_lines.append(cat_line)
    
    icat = 1
    nvotes1 = []
    for cat_line in cat_lines:
        matches = inner.finditer(cat_line)
        sum = 0
        for match in matches:
            start, end = match.span()
            n = int(cat_line[start+1:end-1])
            nvotes1.append([icat,n])
        icat += 1
    
    return nvotes1
    
def proj(nvotes, verbose=False):
    model = [1, .95,.75,.6, .5, .4, .25, .05, 0.]
    nblue = 0
    for vote in nvotes:
        r = random.random()
        cat = vote[0]
        if r<model[cat]:
            nblue += vote[1]
            if verbose:
                print(f'blue {r} {model[cat]}')
        else:
            if verbose:
                print("red")   
    return nblue

#Presidential
simulate = False
reader = PyPDF2.PdfFileReader('election/cook.pdf')
page = reader.getPage(0)
c = page.extractText()
nvotes = parse_pdf(c)

#There are a total of 538 electoral votes
sum=0
for it in nvotes:
    sum += it[1]
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
#320.506 0.5957360594795539 (1000 runs)
print(sum/nruns, sum/(nruns*538))
print(f'blue {nblue} red {nred} tie {ntie}')

#Senate
nvotes=[]
#B=0
#SB=1
#LIB=2
#LEB=3
#T=4
#LER=5
#LIR=6
#SR=7
#R=8

sv=[]
#LIR,R USA,Alabama: 
sv.append([6,8])
#LIR,R USA,Alaska: 
sv.append([  6,8])
#LID,B  USA,Arizona: 
sv.append([  2,0])
#SR,R USA,Arkansas: 
sv.append([  7,8])
#DDUSA,California: 
sv.append([  0,0])
#LID,D, USA,Colorado: 
sv.append([  2,0])
#BB USA,Connecticut: 
sv.append([  0,0])
#SB,B USA,Delaware: 
sv.append([  1,0])
#RR USA,Florida: 
sv.append([  8,8])
#T, LED USA,Georgia: 
sv.append([  4,3])
#BB USA,Hawaii 
sv.append([  0,0])
#SR,R USA,Idaho: 
sv.append([  7,8])
#SB,B USA,Illinois: 
sv.append([  0,1])
#RR USA,Indiana: 
sv.append([  8,8])
#T,R USA,Iowa: 
sv.append([  4,8])
#LIR,R USA,Kansas: 
sv.append([  6,8])
#SR,R USA,Kentucky: 
sv.append([  7,8])
#SR,R USA,Louisiana: 
sv.append([  7,8])
#LED,D USA,Maine: 
sv.append([  3,0])
#BB USA,Maryland: 
sv.append([  0,0])
#SD,B USA,Massachusetts: 
sv.append([  1,0])
#LID,B USA,Michigan: 
sv.append([  2,0])
#LID,B USA,Minnesota: 
sv.append([  2,0])
#LIR,R USA,Mississippi: 
sv.append([  6,8])
#RR USA,Missouri: 
sv.append([  8,8])
#LER,B USA,Montana: 
sv.append([  5,0])
#SR,R USA,Nebraska: 
sv.append([  7,8])
#BB USA,Nevada: 
sv.append([  0,0])
#SD,B USA,New Hampshire: 
sv.append([  1,0])
#SD,B USA,New Jersey: 
sv.append([  1,0])
#SD,D USA,New Mexico: 
sv.append([  1,0])
#BB USA,New York: 
sv.append([  0,0])
#LED,R USA,North Carolina: 
sv.append([  3,8])
#RR USA,North Dakota: 
sv.append([  8,8])
#RB USA,Ohio: 
sv.append([  8,0])
#SR,R USA,Oklahoma: 
sv.append([  7,8])
#SB,B USA,Oregon: 
sv.append([  1,0])
#BR USA,Pennsylvania: 
sv.append([  0,8])
#SB,B USA,Rhode Island: 
sv.append([  1,0])
#LIR,R USA,South Carolina: 
sv.append([  6,8])
#SR,R USA,South Dakota: 
sv.append([  7,8])
#SR,R USA,Tennessee: 
sv.append([  7,8])
#LIR,R USA,Texas: 
sv.append([  7,8])
#RR USA,Utah: 
sv.append([  8,8])
#BB USA,Vermont: 
sv.append([  0,0])
#SD,D USA,Virginia: 
sv.append([  0,1])
#BBUSA,Washington: 
sv.append([  0,0])
#SR,B USA,West Virginia: 
sv.append([  7,0])
#BR USA,Wisconsin: 
sv.append([  0,8])
#SR,R USA,Wyoming: 
sv.append([  7,8])

nd=0
nr=0
for s in sv:
    if s[0]==0:
        nd += 1
    if s[1]==0:
        nd += 1
    if s[0]==8:
        nr += 1
    if s[1]==8:
        nr += 1
print(f'dem continuing {nd} rep continuing {nr}')
nvotes = []
for s in sv:
    nvotes.append([s[0],1])
    nvotes.append([s[1],1])
random.seed(0)
nb=0
nr=0
nt=0
for i in range(1000):
    n=proj(nvotes)
    if n<50:
        nr += 1
    elif n>50:
        nb += 1
    else:
        nt += 1
print(f'blue {nb} red {nr} tie {nt}')
