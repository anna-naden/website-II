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

# df = read_pdf('election/cook.pdf', pages=1)
# solidb = df['Unnamed: 0'][3:]
# likelyb = df['Unnamed: 1'][3:]
# leanb = df['Unnamed: 2'][3:]
# tossup = df['Unnamed: 3'][3:]
# leanr = df['Unnamed: 4'][3:]
# likelyr = df['Unnamed: 5'][3:]
# solidr = df['Unnamed: 6'][3:]

simulate = False
sum=0
j=0
nvotes = []
nblocks = 0
list = \
    [55,7,3,3,4,20,1,10,11,14,5,29,7,4,3,12]
for n in list:
    nvotes.append([0,n])
    sum += n
    nblocks += 1
list = \
    [9,2,13]
for n in list:
    nvotes.append([1,n])
    sum += n
    nblocks += 1
list = \
    [11,16,10,1,6,4,20,10]
for n in list:
    nvotes.append([2,n])
    sum += n
    nblocks += 1
list = \
    [29,16,6,1,15,18,38]
for n in list:
    nvotes.append([3,n])
    sum += n
    nblocks += 1
list = \
    [3,11,6,10,3,9,6]
for n in list:
    nvotes.append([5,n])
    sum += n
    nblocks += 1
list = \
    [9,6,4,8,8,6,2,1,1,3,7,3,11,5,3]
for n in list:
    nvotes.append([6,n])
    sum += n
    nblocks += 1
cook_str = """
14 California (55)
  28,56  324,14 Connecticut (7)
  28,56  310,14 Delaware (3)
  28,56  296,14 Washington DC (3)
  28,56  282,14 Hawaii (4)
  28,56  268,14 Illinois (20)
  28,56  254,14 Maine 1st CD (1)
  28,56  240,14 Maryland (10)
  28,56  226,14 Massachusetts (11)
  28,56  212,14 New Jersey (14)
  28,56  198,14 New Mexico (5)
  28,56  184,14 New York (29)
  28,56  170,14 Oregon (7)
  28,56  156,14 Rhode Island (4)
  28,56  142,14 Vermont (3)
  28,56  128,14 Washington (12)
 134,73  394,14 3 States
 175,23  394,14  
 134,73  366,14 24 Electoral Votes
 134,73  338,14 Colorado (9) 
 134,73  324,14 Maine (2)
 134,73  310,14 Virginia (13) 
 240,91  394,14 7 States
 280,94  394,14  
 284,01  394,14 (+ NE-02)
 240,91  366,14 78 Electoral Votes
 240,91  338,14 Arizona (11) 
 240,91  324,14 Michigan (16)
 240,91  310,14 Minnesota (10) 
 240,91  296,14 Nebraska 2nd CD (1)
 240,91  282,14 Nevada (6)
 240,91  268,14 New Hampshire (4)
 240,91  254,14 Pennsylvania (20) 
 240,91  240,14 Wisconsin (10)
 347,09  394,14 6 States
 387,81  394,14  
 390,89  394,14 (+ ME-02)
 347,09  366,14 123 Electoral Votes
 347,09  338,14 Florida (29) 
 347,09  324,14 Georgia (16)
 347,09  310,14 Iowa (6)
 347,09  296,14 Maine 2nd CD (1)
 347,09  282,14 North Carolina (15)
 347,09  268,14 Ohio (18)
 347,09  254,14 Texas (38)
 453,27  394,93 0 States
 453,27  366,93 0 Electoral Votes
 559,45  394,14 7 States
 559,45  366,14 48 Electoral Votes
 559,45  338,14 Alaska (3)
 559,45  324,14 Indiana (11)
 559,45  310,14 Kansas (6)
 559,45  296,14 Missouri (10)
 559,45  282,14 Montana (3)
 559,45  268,14 South Carolina (9)
 559,45  254,14 Utah (6)
 665,63  394,14 13 States
 710,64  394,14  
 713,71  394,14 (+ NE-01 & 
 665,63  380,14 NE-03)
 665,63  366,14 77 Electoral Votes
 665,63  338,14 Alabama (9)
 665,63  324,14 Arkansas (6)
 665,63  310,14 Idaho (4)
 665,63  296,14 Kentucky (8)
 665,63  282,14 Louisiana (8)
 665,63  268,14 Mississippi (6)
 665,63  254,14 Nebraska (2)
 665,63  240,14 Nebraska 1st CD (1)
 665,63  226,14 Nebraska 3rd CD (1)
 665,63  212,14 North Dakota (3)
 665,63  198,14 Oklahoma (7)
 665,63  184,14 South Dakota (3)
 665,63  170,14 Tennessee (11)
 665,63  156,14 West Virginia (5)
 665,63  142,14 Wyoming (3)
"""
# for cat in [solidb, likelyb, leanb, tossup, leanr, likelyr, solidr]:
#     for i in range(3,len(cat.array)):
#         s=cat[i]
#         if type(s) != type(1.0):
#             nblocks += 1
#             beg = s.find('(')
#             end = s.find(')')
#             n=int(s[beg+1:end])
#             sum += n
#             if simulate:
#                 nvotes.append([3,10])
#             else:
#                 nvotes.append([j,n])
#             print(j,s,n)
#     j += 1

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