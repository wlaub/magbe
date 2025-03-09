import sys, os
import time
import json
import copy
import pprint
import random

from collections import defaultdict

import tabulate
import pyperclip

from slpp import slpp as lua

from PIL import Image

decals_dir = '../../waldmo/Graphics/Atlases/Gameplay/decals/iambad/magbe/rect'

data_file = 'myrotclusters.json'

from prompt_toolkit import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout import ScrollablePane
from prompt_toolkit.layout.containers import VSplit, HSplit, Window
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.widgets import Label, VerticalLine, HorizontalLine
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding import KeyBindings


global_list = FormattedTextControl()
room_list = FormattedTextControl()




all_decals = set()
for dirpath, dirnames, filenames in os.walk(decals_dir):

    decal_path = dirpath
    for name in filenames:
        if name[-4:] != '.png': continue
        decal_name = decal_path+'/'+name[:-4]
        all_decals.add(decal_name)

template = """
    {{
        _fromLayer = "decalsBg",
        color = "ffffff",
        rotation = 0,
        scaleX = 1,
        scaleY = 1,
        texture = "decals/iambad/magbe/rect/{name}",
        x = {xpos},
        y = 0
    }}
"""

class Decal():
    def __init__(self, path):
        self.path = path

        self.name = self.path.split('/')[-1]

    def to_text(self, xoff):
        return template.format(name=self.name, xpos=xoff)

class DecalInstance():
    def __init__(self, decal, data):
        self.data = data
        self.decal = decal

    def to_json(self):
        return {'path':self.decal.path, 'data':self.data}

    @staticmethod
    def from_json(data, decal_map):
        path = data['path']
        decal = decal_map[path]
        return DecalInstance(decal, data['data'])

    def __str__(self):
        return self.decal.name

class DecalMachine():

    def __init__(self):
        decals = []
        self.decal_map = {}
        for path in all_decals:
            decal = Decal(path)
            if decal.name[-1] in {'l','r','u','t'}:
                continue


            decals.append(decal)
            self.decal_map[path] = decal

        decals = tuple(decals)
        self.decals = decals

        self.active_options = list(decals)

        self.clusters = {}

    def save(self, filename):

        data = {
            'clusters':{k:[x.to_json() for x in v] for k,v in self.clusters.items()},
            }
        with open(filename, 'w') as fp:
            json.dump(data, fp, indent=2)

    def load(self, filename):
        with open(filename, 'r') as fp:
            data = json.load(fp)

        self.clusters = clusters = {}
        for name, cluster in data['clusters'].items():
            clusters[int(name)] = [DecalInstance.from_json(x, self.decal_map) for x in cluster]

        self.process_selection()

    def process_selection(self):
        counts = defaultdict(lambda: 0)
        for cluster in self.clusters.values():
            for decal in cluster:
                counts[decal.decal]+=1

        top = max(counts.values())
        remaining = [k for k in self.decals if counts[k] < top]
        self.active_options = remaining

        self.update_lists()

    def pick_next(self):
        if len(self.active_options) == 0:
            self.active_options = list(self.decals)


        result = random.choice(self.active_options)
        self.active_options.remove(result)
        return result

    def get_some(self, n):
        result = [self.pick_next() for _ in range(n)]
        return result

    def update_lists(self):
        lines = []
        for name, cluster in self.clusters.items():
            parts = [str(x) for x in cluster]
            text = f'{name}: {parts}'
            lines.append(text)
        global_list.text = '\n'.join(lines)

        room_list.text = '\n'.join([x.name for x in self.active_options])


    def copy(self):

        parts = dm.get_some(10)

        lines = [x.to_text(i*32) for i,x in enumerate(parts)]

        text = '{'+','.join(lines)+'}'

        pyperclip.copy(text)

        self.update_lists()

    def paste(self):

        text = pyperclip.paste()

        decals = lua.decode(text)
        if not isinstance(decals, list):
            return

        cluster = []
        for entry in decals:
            name = entry['texture'].split('/')[-1]
            path = os.path.join(decals_dir, name)
            decal = self.decal_map[path]
            di = DecalInstance(decal, entry)
            cluster.append(di)

        decals = set(x.decal for x in cluster)
        for other_cluster in self.clusters.values():
            other_decals = set(x.decal for x in other_cluster)
            if decals == other_decals:
                return

        if len(self.clusters) == 0:
            self.clusters[0] = cluster
        else:
            name = max(self.clusters.keys())+1
            self.clusters[name] = cluster

        self.save(data_file)

        self.update_lists()
#        global_list.text = str(cluster)


dm = DecalMachine()
if os.path.exists(data_file):
    dm.load(data_file)

dm.update_lists()

root_container = HSplit([
   VSplit([
        ScrollablePane(content=Window(content=global_list)),
        VerticalLine(),
        ScrollablePane(content=Window(content=room_list)),
        ]),
])
layout = Layout(root_container)

kb = KeyBindings()
@kb.add('c-q')
def exit_(event):
    event.app.exit()
@kb.add('c-c')
def copy_(event):
    dm.copy()
@kb.add('c-v')
def paste_(event):
    dm.paste()
@kb.add('f5')
def refresh_(event):
    dm.process_selection()




app = Application(layout=layout, full_screen=True, key_bindings=kb, mouse_support=True)
app.run()














