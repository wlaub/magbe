import re

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

class Stem():
    def __init__(self, config, room):
        self.room = room
        self.config = config

        m = re.match('(\d+)(.*)', config)
        height, flags = m.groups()

        self.height = int(height)
        self.flags = tuple(flags)

with open('stems.txt', 'r') as fp:
    raw = fp.read()

lines = [x.strip() for x in raw.split('\n') if x.strip() != '']

rooms = []
stems = []

active_room = None
for line in lines:
    if line[0] == '#':
        active_room = Room(line)
        rooms.append(active_room)
    else:
        stem= Stem(line, active_room)
        stems.append(stem)
        if not 'h' in stem.flags:
            pass
        else:
            pass

hcount = len([x for x in stems if 'h' in x.flags])

print(f'{len(stems)} total stems')
print(f'{hcount} hazard stems')

shape_counts = defaultdict(lambda:0)
normal_counts = defaultdict(lambda:0)
hazard_counts = defaultdict(lambda:0)
special_counts = defaultdict(lambda:0)
rooms_map = defaultdict(set)
for stem in stems:
    shape_counts[stem.height] += 1
    rooms_map[stem.height].add(stem.room.name)
    if 's' in stem.flags:
        special_counts[stem.height] += 1
        continue

    if 'h' in stem.flags:
        hazard_counts[stem.height] += 1
    else:
        normal_counts[stem.height] += 1

norm_heights = len(normal_counts)
haz_heights = len(hazard_counts)
spec_heights = len(special_counts)
print(f'{norm_heights} different normal heights')
print(f'{haz_heights} different hazard heights')
print(f'{spec_heights} different special heights')

heights = set(normal_counts.keys())
heights.update(hazard_counts.keys())
heights.update(special_counts.keys())


rows = []
for h in sorted(heights):
    rows.append([
        h,
        normal_counts.get(h, '-'),
        hazard_counts.get(h, '-'),
        special_counts.get(h, '-'),
        ])

print(tabulate.tabulate(rows))

#print(f'Normals: {sorted(normal_counts.items())}')
#print(f'Hazards: {sorted(hazard_counts.items())}')

