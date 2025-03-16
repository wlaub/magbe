import sys, os
import math


import soundfile as sf

from matplotlib import pyplot as plt

source_dir = '../../iwse/sources/synth'
output_dir = '../../iwse/sources/synthloops'

#for 7-minute loops
PAD = 0.00
W = 0.1
DUR = 7*60
XFADE= 0.1

#for 1-minute loops
PAD = 0.10
W = 0.5
DUR = 1*60
XFADE= 0.1

#for 1-minute surges
#TODO

#for shroom
filemap = {
'ultralow_1': '0',
'hyperlow_1': '1',
'low_1': '2',
'mid_1': '3',
'high_1': '4',
}


key = 'iwse_thorns_'

files = os.listdir(source_dir)

pitches = ['ultralow', 'hyperlow', 'low', 'mid', 'high', 'superhigh', 'hyperhigh', 'ultrahigh', 'mosthigh', 'mosthigher']
fmap = {}
for file in files:
    if not key in file: continue
    ext = file[len(key):-4]
    pitch, idx = ext.split('_')
    fmap.setdefault(pitch, []).append((file, idx))

filemap = {}
idx = 0
for pitch in pitches:
    if not pitch in fmap.keys(): continue
    for file, fidx in sorted(fmap[pitch]):
        filemap[pitch+'_'+fidx] = str(idx)
        idx += 1

#for j in range(7):

#    filename = f'iwse_shroom_{j}.wav'

for infile, outfile in filemap.items():

    filename = f'{key}{infile}.wav'
    outfile = f'{key}{outfile}.wav'

    path = os.path.join(source_dir, filename)


    data, fs = sf.read(path)

    left = round(fs*PAD)
    right = left + round(fs*W)
    end = DUR*fs

    xvals = list(range(left, right))
    yvals = []
    yvals2= []
    yvals3= []

    for idx in xvals:
        pl = data[idx]-1
        l = data[idx]
        r = data[idx+end]
        ar = data[idx+end+1]

        dist = 0
        for a,b,c,d in zip(pl, l, r, ar):
            dist+= ((c-b)-(b-a))**2+((c-b)-(d-c))**2

        dist2 = 1000*(l[1]-l[0])**2+(r[1]-r[0])**2
    #    print(idx, dist, dist2)
        yvals.append(dist)
        yvals2.append(dist2)
        yvals3.append(dist+dist2)

    bests =list(sorted(zip(xvals, yvals3), key = lambda x: x[1]))[:10]


    fig, ax = plt.subplots()
    ax2 = ax.twinx()
    ax.scatter(xvals, yvals, s=2, c='k')
    ax2.scatter(xvals, yvals2, s=2, c='r')
    ax2.scatter(xvals, yvals3, s=3, c='b')
    ax2.scatter(*list(zip(*bests)), s=4, c='g')

#    plt.show()


    start_idx, _ = bests[0]

    start_off = start_idx/fs
    print(f'Cutting {filename} at {start_off*1000:0.1f} ms')

    data = data[start_idx:]

    nfade = round(fs*XFADE)

    for idx in range(nfade):
        a = idx/nfade

        l = data[idx]
        r = data[idx+end]

        for i in [0,1]:
            data[idx][i] = l[i]*a+r[i]*(1-a)

    data = data[:end]

    outpath = os.path.join(output_dir, outfile)
    if outpath == path:
        raise RuntimeError('Path failure')

    sf.write(outpath, data, fs)

