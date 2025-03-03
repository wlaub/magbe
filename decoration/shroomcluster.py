import sys, os
import time
import json
import copy
import pprint
import random

from collections import defaultdict

import tabulate

from PIL import Image

decals_dir = '../../waldmo/Graphics/Atlases/Gameplay/decals/iambad/magbe/gmush'

all_decals = set()
for dirpath, dirnames, filenames in os.walk(decals_dir):

    decal_path = dirpath
    for name in filenames:
        if name[-4:] != '.png': continue
        decal_name = decal_path+'/'+name[:-4]
        all_decals.add(decal_name)

def map_height(h):
    if h == 4:
        h = 5
    if h == 8:
        h = 7
    return h

class Decal():
    def __init__(self, path):
        self.path = path

        self.name = self.path.split('/')[-1]

        self.n, self.idx, self.color, _ = self.name.split('.')

        self.basename = self.n+'.'+self.idx

        self.image = Image.open(self.path+'.png')
        iw,ih = self.image.size
        l,t,r,b = self.image.getbbox()
        self.w = r-l
        self.h = b-t
        self.h = map_height(self.h)

class DecalMachine():

    def __init__(self):
        colors = set()
        heights = set()

        height_map = defaultdict(lambda: defaultdict(set))

        decals = []
        for path in all_decals:
            decal = Decal(path)
            decals.append(decal)

            colors.add(decal.color)
            heights.add(decal.h)

            height_map[decal.h][decal.n].add(decal.basename)

        for k,v in height_map.items():
            height_map[k] = {a:list(b) for a,b in v.items()}

        self.height_map = height_map
        self.active_height_map = copy.deepcopy(height_map)

        self.n_options = ['1','2','3']
        self.active_n_options = list(self.n_options)

        self.heights = list(heights)
        self.colors = list(colors)
        self.active_colors = list(colors)

    def pick_next(self, h):
        options = self.active_height_map[h]

        for n in self.active_n_options:
            if n in options.keys():
                break
        else:
            self.active_n_options = list(self.n_options)

        n_options = [x for x in self.active_n_options if x in options.keys()]
        n = random.choice(n_options)
        self.active_n_options.remove(n)

#        print(h, self.active_n_options, n_options, n, options[n])

        res = random.choice(options[n])
        options[n].remove(res)
        if len(options[n]) == 0:
            self.active_height_map[h][n] = copy.deepcopy(self.height_map[h][n])


        color = random.choice(self.active_colors)
        self.active_colors.remove(color)
        if len(self.active_colors) == 0:
            self.active_colors = list(self.colors)

        full_res = res+ '.' + color

        return res, full_res

dm = DecalMachine()


"""
for h in [4,5,6,7,8,9,10]:
    print(h, dm.height_map[h].keys(), [(x, len(dm.height_map[h][x])) for x in dm.height_map[h].keys()])
4  1        2
5  1        4
6  1 2      2+1
7  1        2
8  1  3     1+2
9  1 2 3    1+2+5
10 1 2      2+4
"""

shapes = [
[4,5,6,9,8,10,6,7,5,4],
[5,6,9,8,9,7,5,4,6],

[4,6,9,6,10,7,4,5],
[4,6,10,7,9,6,5],
[6,9,6,10,7,4,5],

[6,7,9,10,9,5],
[6,7,9,10,9,7,4],
[6,8,10,9,7,5],
[4,7,8,5,6,6],
]

active_shapes = list(shapes)

seqs = []
simp_seqs = []

for i in range(61):
    seq = []
    sseq = []
    shape = random.choice(active_shapes)
    active_shapes.remove(shape)
    if len(active_shapes) == 0:
        active_shapes = list(shapes)

    for h in shape:
        h = map_height(h)
        base, full = dm.pick_next(h)
        seq.append(full)
        sseq.append(base)

    if sseq in simp_seqs:
        print('collision')
    else:
        simp_seqs.append(sseq)
        seqs.append(seq)

for idx, seq in enumerate(seqs):
    print(idx, seq)

#a = (21+5)+(29+9+15+21+4+21)+(6+14+30+68)+(24+31+13+20+49+14)+(28)
#print(a/5)
#84.4

#or 34ish more spread out
#+20 for tops
#+7 for underside extras
# = 61 (nice)

#for h in [6,7,9,10,9,5]:
#    print(dm.pick_next(h))
















