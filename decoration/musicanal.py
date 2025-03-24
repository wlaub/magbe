import sys, os
import time
import math
import json
import datetime

from collections import defaultdict

import tabulate

from matplotlib import pyplot as plt
from matplotlib import widgets

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

        if not 'twm' in self.name:
            try:
                self.variant = int(self.name[-2:])
                self.layer = self.name[:-2]
            except:
                self.variant = int(self.name[-1:])
                self.layer = self.name[:-1]
        else:
            self.variant=0
            self.layer = self.name

        if self.x < 0:
            if self.y<500:
                self.group = 'left'
            else:
                self.group = 'scrap'
            if self.layer == 'swoop' and self.x<2400-MIDDLE:
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
        """
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
        """

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

        self.plot_items = items = []
        for layer, variants in self.layer_variants.items():
            for variant, sources in variants.items():
                items.append((layer, variant))

        self.plot_items = sorted(items)
        self.plot_idx = 0

    def hello(self, layer):

        for variant, sources in self.layer_variants[layer].items():
            sources = [x for x in sources if x.group in {'right', 'left'}]
            xvals = [x.phase for x in sources]
            yvals = [-x.y for x in sources]
            size = [8 if x.group == 'left' else 2 for x in sources]


            plt.scatter(xvals, yvals, s=size)

        plt.show()


    def plot_variant(self, idx, ax):

        ax.clear()

        layer, variant = self.plot_items[idx]

        groups = {
        ('left'): {
            'marker': 'o',
            's': 16,
            'c': 'r'
            },
        ('right'): {
            'marker': 'o',
            's': 16,
            'c': 'b'
            },
        ('up', 'down'): {
            'marker': 'o',
            's': 16,
            'c': 'k'
            },
        }

        for sub_groups, pk in groups.items():

            sources = self.layer_variants[layer][variant]
            sources = [x for x in sources if x.group in sub_groups]
            phases = [x.phase for x in sources]
            if len(phases) == 0:
                continue
            pk = dict(pk)

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
            ax.scatter(c, s, **pk)

            for x,y, src in zip(c, s, sources):
                ax.text(x,y, str(src.id))

            cavg = math.cos(pavg*math.pi*2)
            savg = math.sin(pavg*math.pi*2)

            pk['marker'] = 'x'
            pk['s']*=4
            ax.scatter(cavg, savg, **pk)
            ax.set_title(f'{layer}_{variant}')
            ax.set_xlim([-1.1,1.1])
            ax.set_ylim([-1.1,1.1])


        ax.grid(True)
        plt.draw()


    def inc_plot(self, amt, ax):
        self.plot_idx += amt
        if self.plot_idx < 0:
            self.plot_idx += len(self.plot_items)
        elif self.plot_idx > len(self.plot_items)-1:
            self.plot_idx -= len(self.plot_items)
        self.plot_variant(self.plot_idx, ax)

dm = DecalMachine(filename)

fig, ax = plt.subplots()

buttons = []

def next_func(event):
    dm.plot_idx += 1
    dm.plot_variant(dm.plot_idx, ax)

my_next = widgets.Button(fig.add_axes([.9, .1, .1, .1]), 'Next')
my_next.on_clicked(lambda x: dm.inc_plot(1, ax))
my_prev = widgets.Button(fig.add_axes([.9, .2, .1, .1]), 'Prev')
my_prev.on_clicked(lambda x: dm.inc_plot(-1, ax))

def format_coord(x, y):
    phase = math.atan2(y,x)/(math.pi*2)
    if phase < 0:
        phase += 1
    phase_text = str(datetime.timedelta(seconds = phase*7*60))
    return f'{phase:%} | {phase_text}'

ax.format_coord = format_coord

dm.plot_variant(0, ax)

plt.show()

exit()


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




