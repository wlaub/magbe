import sys, os
import math


import soundfile as sf
import numpy as np

from matplotlib import pyplot as plt

source_dir = '../../iwse/sources/synth'
output_dir = '../../iwse/sources/synthloops'

#for 7-minute loops
PAD = 0.00
W = 0.1
DUR = 7*60
XFADE= 0.1

#for 1-minute loops
PAD = 0.001
W = 0.1
DUR = 1*60
XFADE= 0.05
GAIN = 4

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


key = 'iwse_twm_'

files = os.listdir(source_dir)

pitches = ['ultralow', 'hyperlow', 'low', 'mid', 'high', 'superhigh', 'hyperhigh', 'ultrahigh', 'gigahigh','mosthigh', 'mosthigher']
fmap = {}
for file in files:
    if not key in file: continue
    ext = file[len(key):-4]
    parts = ext.split('_')
    pitch = '_'.join(parts[:-1])
    channel = parts[-1]
    fmap.setdefault(pitch, []).append((file, channel))


print(fmap)

settings_map = {
'burst': {
#    'pad': 230.02,
    'pad': 230.52,
    'w': 0.1,
    'dur':7*60+4/44100,
    'xfade': 0.1,
    },
'drone': {
    'pad': 0.001,
    'w': 0.1,
    'dur':7*60,
    'xfade': 0.1,
    },
'melody': {
    'pad': 0.001,
    'w': 0.1,
    'dur':7*60,
    'xfade': 0.1,
    },
'shriek': {
    'pad': 0.001,
    'w': 0.1,
    'dur':7*60,
    'xfade': 0.1,
    },
'sparkles': {
    'pad': 303,
    'w': 0.5,
    'dur':7*60,
    'xfade': 4,
    },
'meat': {
    'pad': 4*60+44.8,
    'w': 0.5,
    'dur':7*60,
    'xfade': 4,
    },
'extra_meat': {
    'pad': 12*60+55.6,
    'w': 0.5,
    'dur':7*60,
    'xfade': 4,
    },





}




for name, channels in fmap.items():

    settings = settings_map.get(name, {})
    if settings == {}: continue
    #for 1-minute loops
    PAD = settings.get('pad', 0.001)
    W = settings.get('w', 0.1)
    DUR = settings.get('dur', 60)
    XFADE= settings.get('xfade', 0.1)
    GAIN = settings.get('gain', 1)

    outfile = f'{key}{name}.wav'

    merge_data = {}
    for filename, channel in channels:
        print(filename)

        path = os.path.join(source_dir, filename)
        data, fs = sf.read(path)

        merge_data[channel] = (data, fs)

    data = np.stack([merge_data['l'][0], merge_data['r'][0]], axis=1)
    print(data[0])

    left = round(fs*PAD)
    right = left + round(fs*W)
    end = round(DUR*fs)

    xvals = list(range(left, right))
    yvals = []
    yvals2= []
    yvals3= []

    for idx in xvals:
        pl = data[idx-1]
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
    print(f'Cutting at {start_off*1000:0.1f} ms {filename} -> {outfile}')

    data = data[start_idx:]

    nfade = round(fs*XFADE)

    for idx in range(nfade):
        a = idx/nfade

        l = data[idx]
        r = data[idx+end]

        for i in [0,1]:
            data[idx][i] = l[i]*a+r[i]*(1-a)

    data = data[:end]

    GAIN = 1/np.max(np.abs(data))

    if GAIN > 1:
        data*=GAIN

    outpath = os.path.join(output_dir, outfile)
    if outpath == path:
        raise RuntimeError('Path failure')

    sf.write(outpath, data, fs)

