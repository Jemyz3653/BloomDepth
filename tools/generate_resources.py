#!/usr/bin/env python3
"""Build original volumetric flower models for Minecraft 26.3."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import random
from zipfile import ZipFile
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'src/main/resources/assets'
MC = ASSETS/'minecraft'
OWN = ASSETS/'bloomdepth'
DISPLAY = {
    'gui': {'rotation':[26,35,0], 'translation':[0,0,0], 'scale':[0.86]*3},
    'ground': {'translation':[0,2,0], 'scale':[0.44]*3},
    'fixed': {'rotation':[0,180,0], 'scale':[0.85]*3},
    'firstperson_righthand': {'rotation':[0,-40,0], 'translation':[1,3,0], 'scale':[0.5]*3},
    'firstperson_lefthand': {'rotation':[0,40,0], 'translation':[1,3,0], 'scale':[0.5]*3},
    'thirdperson_righthand': {'rotation':[65,40,0], 'translation':[0,2,0], 'scale':[0.5]*3},
    'thirdperson_lefthand': {'rotation':[65,-40,0], 'translation':[0,2,0], 'scale':[0.5]*3},
}

# (geometry, visible height, petal, petal shadow, center, stem)
SMALL = {
    'dandelion': ('pom', 11.5, '#f6d73a', '#cd8d1d', '#fbe975', '#5c8239'),
    'golden_dandelion': ('star', 12.2, '#ffe250', '#d79222', '#fff4ae', '#799449'),
    'poppy': ('poppy', 12, '#d83137', '#a3202f', '#33242a', '#47803c'),
    'blue_orchid': ('orchid', 13.4, '#56b9dc', '#315ea7', '#eef7da', '#43756c'),
    'allium': ('allium', 14.2, '#c795dc', '#935ca9', '#f3c6eb', '#637e40'),
    'azure_bluet': ('bluet', 9, '#e3ecdf', '#b8c8ba', '#e9ba36', '#6a8a43'),
    'red_tulip': ('tulip', 13, '#dd3e51', '#a4243d', '#f2b343', '#578545'),
    'orange_tulip': ('tulip', 13, '#f28d39', '#be5831', '#ffcd63', '#578545'),
    'white_tulip': ('tulip', 13, '#eeeee1', '#c3d1d0', '#eee09b', '#578545'),
    'pink_tulip': ('tulip', 13, '#ee9ab8', '#c56391', '#ffddab', '#578545'),
    'oxeye_daisy': ('daisy', 11.4, '#f5f0dc', '#cbd4ca', '#e9bc3e', '#5a8c48'),
    'cornflower': ('corn', 12.7, '#497ae0', '#344da8', '#859cf0', '#547d4d'),
    'lily_of_the_valley': ('bells', 13, '#e7f1e3', '#b0c5c3', '#d4cf80', '#578547'),
    'wither_rose': ('wither', 12.7, '#3e3443', '#211a29', '#8f4150', '#413943'),
    'torchflower': ('torch', 14, '#f0a14b', '#bb3c45', '#ffd96b', '#52846e'),
    'open_eyeblossom': ('eye', 11.8, '#9da49c', '#5e6964', '#f28e38', '#6c7867'),
    'closed_eyeblossom': ('bud', 10.8, '#9da49c', '#667271', '#53635b', '#6c7867'),
}

TALL = {
    'sunflower': ('sun', '#ffcd43', '#d89223', '#754a2d', '#568747'),
    'lilac': ('lilac', '#d4a1d6', '#a66bb6', '#f0bfe2', '#657f47'),
    'rose_bush': ('roses', '#da4052', '#90273a', '#ef7780', '#4b7943'),
    'peony': ('peony', '#e7a1bb', '#bc688f', '#f6c5ce', '#5e8849'),
    'pitcher_plant': ('pitcher', '#5eaeac', '#475d9c', '#df90bf', '#566fa2'),
}

def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n')

def box(x,y,z,X,Y,Z,tex,rotation=None):
    e={'from':[x,y,z],'to':[X,Y,Z],
       'faces':{d:{'texture':'#'+tex} for d in ('down','up','north','south','west','east')}}
    if rotation:
        origin,axis,angle=rotation
        e['rotation']={'origin':origin,'axis':axis,'angle':angle}
    return e

def leaf(x,y,z,length,width,angle,axis='z'):
    return box(x-width/2,y-.38,z-length/2,x+width/2,y+.38,z+length/2,
               'leaf',([x,y,z],axis,angle))

def petals(x,y,z,r=2.7,p=1.1,depth=1.2,core=1.5,shade=False):
    out=[box(x-core,y-.28,z-core,x+core,y+depth,z+core,'petal_dark')]
    for i,(dx,dz) in enumerate(((0,-1),(1,0),(0,1),(-1,0))):
        w=p if dx==0 else (r-core)/2+.6
        l=p if dz==0 else (r-core)/2+.6
        X=x+dx*(r+core)/2
        Z=z+dz*(r+core)/2
        out.append(box(X-w,y-.38,Z-l,X+w,y+depth-.34,Z+l,'petal_dark' if shade and i==1 else 'petal'))
    out.append(box(x-core*.62,y+depth-.3,z-core*.62,x+core*.62,y+depth+.22,z+core*.62,'center'))
    return out

def cup(x,y,z,wide=2.5,high=3):
    w=wide
    return [box(x-w+.5,y-.65,z-w+.5,x+w-.5,y+.45,z+w-.5,'petal_dark'),
            box(x-w,y,z-w,x+w,y+high,z-w+.9,'petal'),
            box(x-w,y,z+w-.9,x+w,y+high-.25,z+w,'petal'),
            box(x-w,y,z-w+.85,x-w+.9,y+high,z+w-.85,'petal_dark'),
            box(x+w-.9,y,z-w+.85,x+w,y+high-.2,z+w-.85,'petal'),
            box(x-.72,y+.12,z-.72,x+.72,y+high*.55,z+.72,'center')]

def stem(x,z,height,width=1.05):
    return box(x-width/2,0,z-width/2,x+width/2,height,z+width/2,'stem')

def small_form(style,h):
    x=z=8
    out=[stem(x,z,h-1)]
    out+= [leaf(6.3,h*.35,8.4,3.2,4.0,-22.5),leaf(9.6,h*.57,7.6,3.0,3.8,22.5)]
    y=h-2
    if style=='tulip':
        return out+cup(x,h-3.3,z,2.45,3.3)
    if style=='poppy':
        return out+petals(x,y,z,3.4,1.7,1.55,1.55,True)
    if style in ('daisy','star','corn'):
        out+=petals(x,y,z,3.5 if style=='daisy' else 3,1.15 if style=='daisy' else .9,1.15)
        if style!='daisy':
            out+= [box(6.05,y-.55,6.1,9.95,y+.4,9.9,'petal',([8,y,8],'y',45))]
        return out
    if style in ('pom','allium'):
        return out+petals(x,y-.65,z,2.8,1.1,1.4,1.6)+[
            box(6.9,y+.45,6.9,9.1,y+1.9,9.1,'petal'),
            box(7.5,y+1.85,7.5,8.5,y+2.15,8.5,'center')]
    if style in ('orchid','bluet'):
        for dx,dz,delta in [(-2.25,-.7,0),(2,.65,-2.1),(0,0,1.4)]:
            out.append(box(min(x,x+dx)-.34,y+delta-.8,min(z,z+dz)-.34,max(x,x+dx)+.34,y+delta+.1,max(z,z+dz)+.34,'stem'))
            out+=petals(x+dx,y+delta,z+dz,1.65 if style=='bluet' else 2.1,.8,1,.9)
        return out
    if style=='bells':
        for dx,dz,delta in [(-2.25,.4,-2.1),(2.05,-.45,-3.1),(-1.55,.3,.1)]:
            Y=y+delta
            out.append(box(min(x,x+dx)-.3,Y+1,min(z,z+dz)-.3,max(x,x+dx)+.3,Y+1.45,max(z,z+dz)+.3,'stem'))
            out.append(box(x+dx-.95,Y-.2,z+dz-.95,x+dx+.95,Y+1,z+dz+.95,'petal'))
            out.append(box(x+dx-.66,Y+1,z+dz-.66,x+dx+.66,Y+1.45,z+dz+.66,'petal_dark'))
        return out
    if style=='wither':
        return out+petals(x,y,z,2.75,.95,1.45,1.25,True)+[
            box(5.6,y-4,7.6,7.6,y-3.3,8.45,'stem',([7.5,y-3.5,8],'z',-22.5))]
    if style=='torch':
        return out+cup(x,y-1.3,z,2.4,3.1)+[
            box(6.4,y-2.1,6.4,9.6,y-.8,9.6,'leaf'),box(7.3,y+.4,7.3,8.7,y+2.7,8.7,'center')]
    if style=='eye':
        return out+petals(x,y,z,2.85,1.28,1.15,1.55)+[
            box(7.3,y+1.18,7.3,8.7,y+1.55,8.7,'center')]
    if style=='bud':
        return out+[box(6.2,y-.55,6.2,9.8,y+1.55,9.8,'petal_dark'),
                    box(6.8,y+1.5,6.8,9.2,y+2.05,9.2,'petal')]
    raise ValueError(style)

def scale(elements, factor, y_offset=0, x_center=8, z_center=8, y_center=0):
    result=[]
    for e in elements:
        def point(p):
            return [round((p[0]-x_center)*factor+8,4),round((p[1]-y_center)*factor+y_offset,4),round((p[2]-z_center)*factor+8,4)]
        q={**e,'from':point(e['from']),'to':point(e['to'])}
        if 'rotation' in e:q['rotation']={**e['rotation'],'origin':point(e['rotation']['origin'])}
        result.append(q)
    return result

def translate(elements, dx, dy, dz):
    result=[]
    for e in elements:
        def add(v):return [round(v[0]+dx,4),round(v[1]+dy,4),round(v[2]+dz,4)]
        q={**e,'from':add(e['from']),'to':add(e['to'])}
        if 'rotation' in e:q['rotation']={**e['rotation'],'origin':add(e['rotation']['origin'])}
        result.append(q)
    return result

def texture(name, base):
    rgb=tuple(bytes.fromhex(base[1:]))
    dest=OWN/'textures'/'block'/f'{name}.png';dest.parent.mkdir(parents=True,exist_ok=True)
    rng=random.Random(int.from_bytes(hashlib.sha256(name.encode()).digest()[:8]))
    im=Image.new('RGB',(16,16))
    for y in range(16):
        for x in range(16):
            tone=1+rng.choice((-.04,-.02,0,0,.018,.037))+(0.023 if name.endswith('_leaf') and abs(x-8)<1 else 0)
            im.putpixel((x,y),tuple(min(255,round(c*tone)) for c in rgb))
    im.save(dest)
    return 'bloomdepth:block/'+name

def palette(name, p, d, c, s):
    rgb=tuple(bytes.fromhex(s[1:]))
    green='#'+''.join(f'{min(255,round(v*1.16)):02x}' for v in rgb)
    return {k:texture(name+'_'+k,v) for k,v in {'petal':p,'petal_dark':d,'center':c,'stem':s,'leaf':green}.items()}

def render_model(root,name,elements,tex,item=False):
    data={'parent':'minecraft:block/block','ambientocclusion':False,'textures':{'particle':tex['petal'],**tex},'elements':elements}
    if item:
        data['display']=DISPLAY
        data['gui_light']='front'
    dump(root/'models'/'block'/f'{name}.json',data)

def item(name,elements,tex):
    render_model(OWN,'item_'+name,elements,tex,True)
    dump(MC/'items'/f'{name}.json',{'model':{'type':'minecraft:model','model':f'bloomdepth:block/item_{name}'}})

def pot(name,elements,tex,pot_elements):
    height=max(p['to'][1] for p in elements)
    width=max(max(abs(p[k][d]-8) for p in elements for k in ('from','to')) for d in (0,2))
    factor=min(.76,10.6/height,4.6/width)
    render_model(MC,'potted_'+name,pot_elements+scale(elements,factor,4.03),
                 {**tex,'flowerpot':'minecraft:block/flower_pot','dirt':'minecraft:block/dirt',
                  'particle':'#flowerpot'})

def tall_form(style):
    lower=[stem(8,8,16,1.4),leaf(5.8,6,8.4,4.8,5.6,-22.5),leaf(10.1,11,7.8,4.8,5.5,22.5)]
    upper=[stem(8,8,9,1.2),leaf(6.5,3.6,8,4.2,4,-22.5)]
    if style=='sun':
        upper=[stem(8,8,9,1.5),leaf(6.3,3.1,8,4.8,5,-22.5)]
        # Sunflower faces east, matching vanilla. Disk and petals have depth.
        upper+=[box(8.5,3.8,3.8,10.15,12.2,12.2,'leaf'),box(10.05,5.1,5.1,11.4,10.9,10.9,'center')]
        for n in range(8):
            a=n*math.pi/4; y=8+math.sin(a)*4.4; z=8+math.cos(a)*4.4
            upper.append(box(9.3,y-1.28,z-1.28,10.85,y+1.28,z+1.28,'petal' if n%2 else 'petal_dark'))
    elif style=='lilac':
        lower+=petals(5.3,13.45,8.8,2,.78,1,.9)
        for x,y,z in [(5.1,8.5,7.5),(10.9,9.5,8.1),(7.35,12.3,8.8),(8.8,15,8.6)]:
            upper.append(stem(x,z,y,.7))
            upper+=petals(x,y,z,2.25,.8,1.15,1)
    elif style=='roses':
        lower+=cup(5.3,10.7,8.4,1.85,2.8)+cup(10.55,13,7.65,1.8,2.7)
        upper+=cup(5.1,5.7,8.45,1.75,2.8)+cup(10.4,8.9,7.9,2.45,3)+cup(7.2,12,8.8,1.9,3)
    elif style=='peony':
        lower.append(leaf(5.4,13.5,8,4.1,6,-22.5))
        for x,y,z in [(5.05,7.1,8.8),(10.65,11.3,7.9),(7.6,14.1,8.4)]:
            upper+=petals(x,y,z,3.05,1.28,1.6,1.55)+cup(x,y+.5,z,1.65,1.7)
    elif style=='pitcher':
        lower=[box(5.45,0,5.6,10.55,4,10.4,'stem'),stem(8,8,16,1.4),
               leaf(5.6,4,8,5.1,5.7,-22.5),leaf(10.1,7.2,8,4.8,5.2,22.5),
               leaf(6.6,10.8,8.9,4.4,4.6,-22.5)]
        upper+=cup(8,2.7,8,2.9,7.6)+[box(5.45,10.3,5.8,10.55,11.25,10.2,'center'),
                box(6.25,11.2,6.2,10.05,13.9,9.8,'petal',([8,11,8],'z',-22.5))]
    return lower,upper

def generate(vanilla):
    with ZipFile(vanilla) as z:
        original=set(z.namelist())
        pot_elements=json.loads(z.read('assets/minecraft/models/block/flower_pot_cross.json'))['elements'][:5]
        small_tag=json.loads(z.read('data/minecraft/tags/item/small_flowers.json'))['values']
        assert {i.split(':')[1] for i in small_tag}==SMALL.keys(), 'Flower list differs from Minecraft 26.3'
    for name,(style,h,*colors) in SMALL.items():
        tex=palette(name,*colors)
        elements=small_form(style,h)
        render_model(MC,name,elements,tex)
        item(name,elements,tex)
        pot(name,elements,tex,pot_elements)
        if name=='torchflower':
            for stage,factor in ((0,.36),(1,.64)):
                render_model(MC,f'torchflower_crop_stage{stage}',scale(elements,factor),tex)
    for name,(style,*colors) in TALL.items():
        tex=palette(name,*colors)
        lower,upper=tall_form(style)
        low_suffix='bottom'
        render_model(MC,name+'_'+low_suffix,lower,tex)
        render_model(MC,name+'_top',upper,tex)
        item(name,scale(lower+translate(upper,0,16,0),.48),tex)
        if name=='pitcher_plant':
            for stage,factor in enumerate((.26,.46,.67,1,1)):
                render_model(MC,f'pitcher_crop_bottom_stage_{stage}',scale(lower,factor),tex)
                if f'assets/minecraft/models/block/pitcher_crop_top_stage_{stage}.json' in original:
                    render_model(MC,f'pitcher_crop_top_stage_{stage}',scale(upper,max(.34,factor)),tex)
    for name,colors in {
        'pink_petals':('#eaa0be','#c270a0','#f8e0a5','#68914f'),
        'wildflowers':('#f3d662','#d2a545','#ffefaa','#75964e'),
    }.items():
        tex=palette(name,*colors);combined=[]
        for i,(x,z,y) in enumerate(((4,4,1.55),(12,4,1.8),(12,12,1.35),(4,12,1.9)),1):
            group=[stem(x,z,y,.66)]+petals(x,y,z,2.4,.82,.67,1.04)
            render_model(MC,f'{name}_{i}',group,tex)
            combined+=group
        item(name,combined,tex)
    tex=palette('cactus_flower','#ef8195','#c25275','#f7d282','#628c50')
    cactus=petals(8,2,8,4.3,2.15,2,2.25)+cup(8,3,8,2.25,2)
    render_model(MC,'cactus_flower',cactus,tex)
    item('cactus_flower',cactus,tex)
    tex=palette('spore_blossom','#e184af','#ab507e','#f0b775','#62954a')
    spore=[box(6.5,12,6.5,9.5,16,9.5,'stem'),box(4,10.2,4,12,12.8,12,'leaf'),
           box(5,8.8,5,11,11,11,'petal_dark'),box(6.3,7.7,6.3,9.7,9.5,9.7,'center')]
    for a in range(8):
        t=a*math.pi/4;x=8+math.cos(t)*3.8;z=8+math.sin(t)*3.8
        spore.append(box(x-1.4,9.5,z-1.4,x+1.4,11.4,z+1.4,'petal',([x,10.5,z],'y',a*45 if a<=1 else (45 if a%2 else 0))))
    render_model(MC,'spore_blossom',spore,tex)
    item('spore_blossom',translate(spore,0,-7,0),tex)
    tex=palette('flowering_azalea','#e899bc','#ba6290','#f2c4d5','#6b8948')
    shrub=[box(6.6,0,6.7,9.4,7,9.3,'stem'),box(2.5,4.9,2.5,13.5,10,13.5,'leaf'),
           box(4,9.7,4,12,13.3,12,'leaf'),box(3.4,12,7,6.2,14,9.7,'leaf')]
    for x,y,z in [(4.6,12.8,7.6),(9.6,13.3,6.25),(10,10.8,11.9),(4.5,9.8,3.8)]:
        shrub+=petals(x,y,z,1.65,.8,.72,.9)
    render_model(MC,'flowering_azalea',shrub,tex)
    item('flowering_azalea',shrub,tex)
    pot('flowering_azalea_bush',shrub,tex,pot_elements)
    tex=palette('mangrove_propagule','#9bb45f','#667f3b','#b9c986','#718f4e')
    seedling=[stem(8,8,8,1.35),leaf(5.8,6.3,8,3.4,4.4,-22.5),leaf(10.05,7.8,8,3.4,4.4,22.5),
              box(7,7.5,7,9,10,9,'petal')]
    render_model(MC,'mangrove_propagule',seedling,tex)
    item('mangrove_propagule',seedling,tex)
    pot('mangrove_propagule',seedling,tex,pot_elements)
    for age in range(5):
        h=2.6+age*1.95
        render_model(MC,f'mangrove_propagule_hanging_{age}',[
            box(7.4,16-h,7.4,8.6,16,8.6,'stem'),box(7,15-h,7,9,17-h,9,'petal')],tex)
    # Chorus flowers keep their nearly full-block silhouette and gain a raised bloom.
    for name, colors in {
        'chorus_flower':('#bd9abe','#8d6895','#edddea','#6d4778'),
        'chorus_flower_dead':('#978794','#705a6d','#c4a9bb','#604764'),
    }.items():
        tex=palette(name,*colors)
        branch=[box(2,0,2,14,2.1,14,'stem'),box(1,2,1,15,12.2,15,'petal_dark'),
                box(2,12.1,2,14,14,14,'petal')]
        bloom=branch+petals(8,14,8,5.2,1.85,1.55,2.8)
        render_model(MC,name,bloom,tex)
        if name=='chorus_flower':
            item(name,bloom,tex)
    print('Generated 29 flower and flowering-plant families, including 19 potted variants.')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('minecraft_client_jar',type=Path)
    generate(parser.parse_args().minecraft_client_jar)
