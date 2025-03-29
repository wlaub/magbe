import sys, os
import math

from collections import defaultdict

from PIL import Image


decals_root = '../../waldmo/Graphics/Atlases/Gameplay/decals/iambad/magbe/'

total_counts = defaultdict(lambda:0)
unfuck_counts = defaultdict(lambda:0)

for dirpath, dirnames, filenames in os.walk(decals_root):
    subdir = dirpath.split('/')[-1]
    if not subdir in {'bgm', 'bgr', 'stem', 'tri', 'ball', 'gill'}:
        continue

    decal_path = dirpath
    for name in filenames:
        if name[-4:] != '.png': continue
        path = os.path.join(decal_path, name)

        image = Image.open(path)

        w,h = image.size

        unfuck = False
        if w%2 == 1:
            w+=1
            unfuck = True
        if h%2 == 1:
            h+=1
            unfuck = True

        if unfuck:
                unfuck_counts[subdir] += 1

        total_counts[subdir] += 1

        if unfuck:
            print(path)
            out_image = Image.new('RGBA', (w,h), (0,0,0,0))

            out_image.paste(image, (0,0))


            out_image.save(path)

#        if unfuck:
#            print(f'Decal {name} requires unfucking')

for name, count in unfuck_counts.items():
    total = total_counts[name]
    print(f'{name} {count}/{total}')

