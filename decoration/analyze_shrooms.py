
from collections import defaultdict

import tabulate

class Room():
    def __init__(self, config):
        config = config[1:]
        self.config = config
        parts = config.split(' ')
        self.name = parts[0]
        if len(parts) > 1:
            self.side = parts[1]

class Shroom():
    N = 7
    def __init__(self, config, room):
        self.room = room
        self.config = config

        self.widths = []
        self.flags = []
        for char in config:
            try:
                w = int(char, 16)
                self.widths.append(w)
            except ValueError:
                self.flags.append(char)

        if len(self.widths) < self.N:
            diff = self.N - len(self.widths)
            base = [0]*diff
            base.extend(self.widths)
            self.widths = base

        self.widths = tuple(self.widths)
        self.flags = tuple(self.flags)

    def get_base_width(self):
        for x in self.widths:
            if x != 0: return x

    def get_top_width(self):
        return self.widths[-1]

    def get_height(self):
        return len([x for x in self.widths if x != 0])

    def get_edge_height(self):
        h = self.get_height()
        if h > 1: h-=1
        return h

with open('shrooms.txt', 'r') as fp:
    raw = fp.read()

lines = [x.strip() for x in raw.split('\n') if x.strip() != '']

rooms = []
shrooms = []
distinct_shapes = set()
normal_gills = defaultdict(lambda: 0)
hazard_gills = defaultdict(lambda: 0)

spike_counts = defaultdict(lambda: 0)

active_room = None
for line in lines:
    if line[0] == '#':
        active_room = Room(line)
        rooms.append(active_room)
    else:
        shroom = Shroom(line, active_room)
        shrooms.append(shroom)
        distinct_shapes.add(shroom.widths)
        if not 'h' in shroom.flags:
            normal_gills[shroom.get_base_width()] += 1
        else:
            hazard_gills[shroom.get_base_width()] += 1
            spike_counts[shroom.get_edge_height()] += 2
            spike_counts[shroom.get_top_width()] += 1

hcount = len([x for x in shrooms if 'h' in x.flags])

print(f'{len(shrooms)} total shrooms')
print(f'{hcount} hazard shrooms')
print(f'{len(distinct_shapes)} different shapes')

distinct_shapes = list(sorted(distinct_shapes))

shape_counts = defaultdict(lambda:0)
hazard_counts = defaultdict(lambda:0)
special_counts = defaultdict(lambda:0)
rooms_map = defaultdict(set)
for shroom in shrooms:
    shape_counts[shroom.widths] += 1
    rooms_map[shroom.widths].add(shroom.room.name)
    if 'h' in shroom.flags:
        hazard_counts[shroom.widths] += 1
    if 's' in shroom.flags:
        special_counts[shroom.widths] += 1

rows = []
for shape in distinct_shapes:
    height = len([x for x in shape if x != 0])
    row = [''.join(f'{x:x}' for x in shape),
            height,
            shape_counts[shape],
            hazard_counts[shape],
            special_counts[shape],
#            rooms_map[shape]
            ]
    rows.append(row)

rows = list(sorted(rows, key = lambda x: (x[1], x[2]), reverse=True ))

print(tabulate.tabulate(rows))

print(f'Normal gills: {sorted(normal_gills.items())}')
print(f'Hazard gills: {sorted(hazard_gills.items())}')
print(f'Spikes: {sorted(spike_counts.items())}')
#for row in rows:
#    print(row[2])

