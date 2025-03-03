import sys, os

import pyperclip


template = """
    {{
        _fromLayer = "decalsBg",
        color = "ffffff",
        rotation = 0,
        scaleX = 1,
        scaleY = 1,
        texture = "decals/iambad/magbe/gmush/{name}.",
        x = {xpos},
        y = 400
    }}
"""


with open('clusters.txt') as fp:
    raw = fp.read()

lines = raw.strip().split('\n')

seqs = {}
for line in lines[14:]:
    parts = line.split(' ')
    idx = parts[0]
    seq = ' '.join(parts[1:])
    seq = eval(seq)

    seqs[idx] = seq


seq = seqs[sys.argv[1]]

decals = []
xpos = 0
for name in seq:
    decal = template.format(name=name, xpos=xpos)
    decals.append(decal)
    xpos += 8

print(seq)

output ='{'+ ','.join(decals)+'}'

pyperclip.copy(output)

