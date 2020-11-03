import pandas as pd
import numpy as np
import re
import random
import json

import PyPDF2
states = 'Alabama|Alaska|Arizona|Arkansas|California|Colorado|Connecticut|Delaware|Florida|Georgia|Hawaii|Idaho|Illinois|Indiana|Iowa|Kansas|Kentucky|Louisiana|Maine|Maryland|Massachusetts|Michigan|Minnesota|Mississippi|Missouri|Montana|Nebraska|Nevada|New Hampshire|New Jersey|New Mexico|New York|North Carolina|North Dakota|Ohio|Oklahoma|Oregon|Pennsylvania|Rhode Island|South Carolina|South Dakota|Tennessee|Texas|Utah|Virginia|Vermont|Washington|West Virginia|Wisconsin|Wyoming'

categories = ['democrat', 'solid democrat', 'likely democrat', 'leans democrat', 'tossup', 'leans republican', 'likely republican', 'solid republican', 'republican']

#Presidential
def parse_pdf(c):
    c=c.replace('\n','')
    i=0
    cats = []

    #Each match has all the data for a given category (solid blue, likely blue, etc.)
    regexpr = r'Electoral Votes'
    outer = re.compile(regexpr)
    
    #Each match has a vote count for one state or state/district combination
    regexpr = r'\(\d+\)'
    re_votes = re.compile(regexpr)

    #Each match is one state
    re_states = re.compile(states)
    
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
        # print(cat_line)
        matches = re_states.finditer(cat_line)
        state_pieces = []
        for match in matches:
            start, end = match.span()
            state_pieces.append(start)
        state_pieces.append(len(cat_line))
        for istate_piece in range(len(state_pieces)-1):
            state_piece = cat_line[state_pieces[istate_piece]:state_pieces[istate_piece+1]]
            # print(state_piece)
            vmatches = re_votes.finditer(state_piece)
            for vmatch in vmatches:
                vstart, vend = vmatch.span()
                n = int(state_piece[vstart+1:vend-1])
                nvotes1.append([icat,n, state_piece, categories[icat]])
        icat += 1
    # with open('election/cook.json', 'w') as f:
    #     json.dump(nvotes1, f, indent=0)
    # f.close()
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
with open('cook.txt', 'w') as f:
    f.write(c)

#Decide whether to use the cook report or use the saved json with possible overrides
get_cook = False
if get_cook:
    nvotes = parse_pdf(c)
else:
    with open('election/overrides.json', 'r') as f:
        nvotes = json.load(f)
    f.close()

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
nbiden = nblue
ntrump = nred
n_pres_tie = ntie

################################################
#Senate
################################################

#Decide whether to load categories collected from 538 site or use overrides
override_senate = False
if not override_senate:
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
    sv.append([6,8, 'AL'])

    #LIR,R USA,Alaska: 
    sv.append([  6,8, 'AK'])

    #LID,B  USA,Arizona: 
    sv.append([  2,0, 'AZ'])

    #SR,R USA,Arkansas: 
    sv.append([  7,8, 'AR Arkansas'])

    #DDUSA,California: 
    sv.append([  0,0, 'CA'])

    #LID,D, USA,Colorado: 
    sv.append([  2,0, 'CO'])

    #BB USA,Connecticut: 
    sv.append([  0,0, 'CT'])

    #SB,B USA,Delaware: 
    sv.append([  1,0, 'DE'])

    #RR USA,Florida: 
    sv.append([  8,8, 'FL']
    )
    #T, LED USA,Georgia: 
    sv.append([  4,3, 'GA'])

    #BB USA,Hawaii 
    sv.append([  0,0, 'HI'])

    #SR,R USA,Idaho: 
    sv.append([  7,8, 'Idaho'])

    #SB,B USA,Illinois: 
    sv.append([  0,1, 'IL'])

    #RR USA,Indiana: 
    sv.append([  8,8, 'Indiana'])

    #T,R USA,Iowa: 
    sv.append([  4,8, 'Iowa'])

    #LIR,R USA,Kansas: 
    sv.append([  6,8, 'Kansas'])

    #SR,R USA,Kentucky: 
    sv.append([  7,8, 'Kentucky'])

    #SR,R USA,Louisiana: 
    sv.append([  7,8, 'LA'])

    #LED,D USA,Maine: 
    sv.append([  3,0, 'ME'])

    #BB USA,Maryland: 
    sv.append([  0,0, 'Maryland'])

    #SD,B USA,Massachusetts: 
    sv.append([  1,0, 'Massachusetts'])

    #LID,B USA,Michigan: 
    sv.append([  2,0, 'Michigan'])

    #LID,B USA,Minnesota: 
    sv.append([  2,0, 'Minnesota'])

    #LIR,R USA,Mississippi: 
    sv.append([  6,8, 'Mississippi'])

    #RR USA,Missouri: 
    sv.append([  8,8, 'Missouri'])

    #LER,B USA,Montana: 
    sv.append([  5,0, 'Montana'])

    #SR,R USA,Nebraska: 
    sv.append([  7,8, 'Nebraska'])

    #BB USA,Nevada: 
    sv.append([  0,0, 'Nevada'])

    #SD,B USA,New Hampshire: 
    sv.append([  1,0, 'New Hampshire'])

    #SD,B USA,New Jersey: 
    sv.append([  1,0, "New Jersey"])

    #SD,D USA,New Mexico: 
    sv.append([  1,0, 'New Mexico'])

    #BB USA,New York: 
    sv.append([  0,0, 'NY'])

    #LED,R USA,North Carolina: 
    sv.append([  3,8, "NC"])

    #RR USA,North Dakota: 
    sv.append([  8,8, 'ND'])

    #RB USA,Ohio: 
    sv.append([  8,0, 'Ohio'])

    #SR,R USA,Oklahoma: 
    sv.append([  7,8, 'Oklahoma'])

    #SB,B USA,Oregon: 
    sv.append([  1,0, 'Oregon'])

    #BR USA,Pennsylvania: 
    sv.append([  0,8, 'PA'])

    #SB,B USA,Rhode Island: 
    sv.append([  1,0, 'Rhode Island'])

    #LIR,R USA,South Carolina: 
    sv.append([  6,8, 'South Carolina'])

    #SR,R USA,South Dakota: 
    sv.append([  7,8, 'South Dakota'])

    #SR,R USA,Tennessee: 
    sv.append([  7,8, 'Tennessee'])

    #LIR,R USA,Texas: 
    sv.append([  7,8, 'TX'])

    #RR USA,Utah: 
    sv.append([  8,8, 'UT'])

    #BB USA,Vermont: 
    sv.append([  0,0, 'VT'])

    #SD,D USA,Virginia: 
    sv.append([  0,1, 'VA'])

    #BBUSA,Washington: 
    sv.append([  0,0, 'WA'])

    #SR,B USA,West Virginia: 
    sv.append([  7,0, 'West Virginia'])

    #BR USA,Wisconsin: 
    sv.append([  0,8, 'Wisconsin'])

    #SR,R USA,Wyoming: 
    sv.append([  7,8, 'Wyoming'])

    sv2 = []
    for v in sv:
        sv2.append([\
            v[0],v[1],v[2], \
            categories[v[0]], \
            categories[v[1]] \
              ] )

    with open('election/senate.json', 'w') as f:
        json.dump(sv2,f, indent=2)
    f.close()
else:
    with open ('election/senate.json', 'r') as f:
        sv = json.load(f)
    f.close()

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
#blue 700 red 140 tie 160

print('---------- PRESIDENTIAL ------------------')
print(f'Biden {nbiden} Trump {ntrump} Tie {n_pres_tie}\n')
print('----------  SENATE -----------------------')
print(f'Democrat majority {nb} Republican majority {nr} Tie {nt}')
