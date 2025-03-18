import sys, os
import math


import soundfile as sf
import numpy as np

from matplotlib import pyplot as plt

source_dir = '../../iwse/sources/ambient'
output_dir = '../../iwse/sources/ambientloops'

settings_map = {
'outdoor_0': {
    'filename': 'outdoor.wav',
    'pad': 60+16.161,
    'w': 1,
    'dur':7*60,
    'xfade': 7,
    },
'outdoor_1': {
    'filename': 'outdoor.wav',
    'pad': 7*60+55,
    'w': 2,
    'dur':7*60+3/44100,
    'xfade': 7,
    },
'outdoor_2': {
    'filename': 'outdoor.wav',
    'pad': 14*60+59.82,
    'w': 2,
    'dur':7*60+3/44100,
    'xfade': 7,
    },
'outdoor_3': {
    'filename': 'outdoor.wav',
    'pad': 22*60+7.671,
    'w': 2,
    'dur':7*60+3/44100,
    'xfade': 7,
    },
'outdoor_4': {
    'filename': 'outdoor.wav',
    'pad': 28*60+56.295,
    'w': 2,
    'dur':7*60+3/44100,
    'xfade': 7,
    },
'pacing_0': {
    'filename': 'pacing.wav',
    'pad': 0*60+31.951,
    'w': 2,
    'dur':7*60+3/44100,
    'xfade': 7,
    },
'pacing_1': {
    'filename': 'pacing.wav',
    'pad': 7*60+38.826,
    'w': 2,
    'dur':7*60+3/44100,
    'xfade': 7,
    },
'pacing_2': {
    'filename': 'pacing.wav',
    'pad': 20*60+5.209,
    'w': 2,
    'dur':7*60+3/44100,
    'xfade': 7,
    },
'vac_0': {
    'filename': 'vacuum.wav',
    'pad': 6*60+29.724,
    'w': 2,
    'dur':7*60+3/44100,
    'xfade': 7,
    },
'vac_1': {
    'filename': 'vacuum.wav',
    'pad': 22*60+26.757,
    'w': 2,
    'dur':7*60+3/44100,
    'xfade': 7,
    },
'vac_2': {
    'filename': 'vacuum.wav',
    'pad': 35*60+16.058-5,
    'w': 2,
    'dur':7*60+3/44100,
    'xfade': 7,
    },
'work_0': {
    'filename': 'work.wav',
    'pad': 3*60+16.534,
    'w': 2,
    'dur':7*60+3/44100,
    'xfade': 7,
    },
'work_1': {
    'filename': 'work.wav',
    'pad': 11*60+54.432,
    'w': 2,
    'dur':7*60+3/44100,
    'xfade': 7,
    },
'work_2': {
    'filename': 'work.wav',
    'pad': 26*60+13.198,
    'w': 2,
    'dur':7*60+3/44100,
    'xfade': 7,
    },
'work_3': {
    'filename': 'work.wav',
    'pad': 40*60+59.086,
    'w': 2,
    'dur':7*60+3/44100,
    'xfade': 7,
    },
'work_4': {
    'filename': 'work.wav',
    'pad': 47*60+11.627,
    'w': 2,
    'dur':7*60+3/44100,
    'xfade': 1.6,
    },
'breath_0': {
    'filename': 'breath.wav',
    'pad': 10.8,
    'w': 2,
    'dur':7*60+3/44100,
    'xfade': 1.6,
    },

'breath_1': {
    'filename': 'breath.wav',
    'pad': 8*60+27.5,
    'w': 2,
    'dur':7*60+3/44100,
    'xfade': 1.6,
    },




}
force = []



for name, settings in settings_map.items():

    PAD = settings.get('pad', 0.001)
    W = settings.get('w', 0.1)
    DUR = settings.get('dur', 60)
    XFADE= settings.get('xfade', 0.1)
    GAIN = settings.get('gain', 1)

    outfile = f'iwse_{name}.wav'
    filename = settings['filename']
    if os.path.exists(os.path.join(output_dir, outfile)) and not name in force:
        print(f'skipping {name}')
        continue


    path = os.path.join(source_dir, filename)
    data, fs = sf.read(path)

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

