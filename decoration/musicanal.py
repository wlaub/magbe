import sys, os
import time
import math
import json

from collections import defaultdict

import tabulate

from matplotlib import pyplot as plt

filename = '/home/wlaub/celeste/olympus/musics_dump.txt'

MIDDLE = 5404

class Source():
    def __init__(self, line):
        self.line = line

        parts = line.split(' ')

        self.name = parts[0]
        self.x = float(parts[1])-MIDDLE
        self.y = float(parts[2])

        self.id = int(parts[3])

        try:
            self.variant = int(self.name[-2:])
            self.layer = self.name[:-2]
        except:
            self.variant = int(self.name[-1:])
            self.layer = self.name[:-1]

        if self.x < 0:
            if self.y<500:
                self.group = 'left'
            else:
                self.group = 'scrap'
        elif self.x < 7092-MIDDLE or (self.y >235 and self.y<397):
            if self.y<500:
                self.group = 'right'
            else:
                self.group = 'scrap'
        elif self.y > 0:
            self.group = 'down'
        else:
            self.group = 'up'

        W = MIDDLE-2278
        W = MIDDLE-3458
        WR = W*0.9
        dp = (7941-MIDDLE)/WR

        if self.group == 'left':
            self.phase = -self.x/W
        elif self.group == 'right':
            self.phase = self.x/WR
        elif self.group == 'up':
            self.phase = dp-(self.y+250)/WR
        elif self.group == 'down':
            self.phase = dp+(self.y-377)/WR
        else:
            self.phase = -1

        if self.phase > 1:
            self.phase -=1

        self.base_phase = None
        if self.layer == 'organ':
            self.base_phase = 1.5/7
        if self.layer == 'shroom':
            self.base_phase = 2/7
        if self.layer == 'swoop':
            self.base_phase = 1.33/7
        if self.layer == 'shard':
            self.base_phase = 1/7

        #get track phase
        if self.base_phase is not None:
            self.phase -= self.base_phase


class DecalMachine():
    def __init__(self, filename):
        self.filename = filename

        self.load()

    def load(self):
        with open(self.filename, 'r') as fp:
            raw=fp.read().strip()

        self.sources = []
        for line in raw.split('\n'):
            try:
                src= Source(line)
                if src.phase != -1:
                    self.sources.append(src)
            except Exception as e:
                print(f'Failed on {line} with {e}')

        layer_variants = defaultdict(lambda: defaultdict(list))
        for source in self.sources:
            layer_variants[source.layer][source.variant].append(source)
        self.layer_variants = layer_variants

    def hello(self, layer):

        for variant, sources in self.layer_variants[layer].items():
            sources = [x for x in sources if x.group in {'right', 'left'}]
            xvals = [x.phase for x in sources]
            yvals = [-x.y for x in sources]
            size = [8 if x.group == 'left' else 2 for x in sources]


            plt.scatter(xvals, yvals, s=size)

        plt.show()


dm = DecalMachine(filename)

for layer, variants in dm.layer_variants.items():
#    if layer not in {'swoop'}:
#        continue
    for variant, sources in variants.items():
        phases = [x.phase for x in sources if x.group in ["left", "right"]]
        if len(phases) == 0:
            continue

        c = [math.cos(x*math.pi*2) for x in phases]
        s = [math.sin(x*math.pi*2) for x in phases]
        cavg = sum(c)/len(c)
        savg = sum(s)/len(s)
        pavg = math.atan2(savg, cavg)/(2*math.pi)
        if pavg < 0:
            pavg += 1

        pmin = min(phases)
        pmax = max(phases)

        print(f'{layer} {variant} {pmin:.2f}|{pavg:.2f}|{pmax:.2f}')
#        print(f'{layer} {variant} {phases}')

#        plt.scatter(c, s, s=4)

#    plt.show()
#dm.hello('organ')




