import glob, os
import time
import json
import random
import math
from collections import defaultdict

import pygame
import pygame.gfxdraw
import pygame.font
from pygame.locals import *

import screeninfo

pygame.init()
pygame.font.init()

font = pygame.font.Font(size=18)

LMB = 1
MMB = 2
RMB = 3

w,h = 1280, 720

screen = pygame.display.set_mode((w, h), pygame.RESIZABLE)

INFILE = "data_in.json"
OUTFILE = "data_out.json"

PXPMM = 1.2581913499344692

class Spinner:
    hitbox = None
    selected_hitbox = None
    @staticmethod
    def init():
        def draw_hitbox(hitbox, c):
            pygame.gfxdraw.polygon( hitbox,
                [(4,2),(11,2),(13,4),(13,11),(11,13),(4,13),(2,11), (2,4)],
                c
                )
            pygame.gfxdraw.polygon( hitbox,
                [(0,5),(15,5),(15,8),(0,8)],
                c
                )
            hitbox.set_colorkey((0,0,0))

        hitbox = Spinner.hitbox = pygame.Surface((16,16))
        draw_hitbox(hitbox, (0,255,0))
        hitbox = Spinner.selected_hitbox = pygame.Surface((16,16))
        draw_hitbox(hitbox, (255,255,255))



    def __init__(self, x, y, a=0, s=8, N=3, eid=0, layer = 0):
        self.x = x
        self.y = y
        self.a = a
        self.eid = eid
        self.layer = layer

        self.N = N
        #0.83 or 1.16
        s = 8-0.5*.84*PXPMM
        self.s = s
        self.r = s/math.cos(math.pi/N)

    def save(self):
        return {
            'x': self.x,
            'y': self.y,
            'a': self.a,
            's': self.s,
            'N': self.N,
            'eid': self.eid,
            'layer': self.layer,
            }

    def neq(self, a):
        return self.x != a.x or self.y != a.y or self.a != a.a or self.s != a.s or self.N != a.N or self.layer != a.layer or self.eid != a.eid

    def render(self, target, xoff, yoff, selected):
        x = self.x-xoff
        y = self.y-yoff

        hitbox = Spinner.selected_hitbox if selected else Spinner.hitbox
        target.blit(hitbox, (x-8,y-8))

#        pygame.gfxdraw.pixel(target, int(x),int(y), (0,0,0))

    def render_shape_back(self, target, xoff, yoff, selected):
        x = self.x-xoff
        y = self.y-yoff

        r = self.r+2
        verts = []
        N = self.N
        for i in range(N):
            a = self.a+i*2*math.pi/N
            verts.append((
                r*math.cos(a)+x,
                r*math.sin(a)+y
                ))

        try:
            c = (0,0,0)
            pygame.gfxdraw.filled_polygon(target, verts, c)
            pygame.gfxdraw.aapolygon(target, verts, c)
        except Exception as e:
            print(e)



    def render_shape(self, target, xoff, yoff, selected, layer):
        x = self.x-xoff
        y = self.y-yoff


        verts = []
        N = self.N
        for i in range(N):
            a = self.a+i*2*math.pi/N
            verts.append((
                self.r*math.cos(a)+x,
                self.r*math.sin(a)+y
                ))

        colors = {0: (255,0,64),
                  1:(128,0,0),
                  }

        try:
            c = colors.get(layer, (255,0,255))
            pygame.gfxdraw.filled_polygon(target, verts, c)
            pygame.gfxdraw.aapolygon(target, verts, c)
        except Exception as e:
            print(e)




    def get_hit(self, x, y):
        r =(self.x-x)**2 + (self.y-y)**2
        if r < 144:
            return r
        return -1

class DragController:
    def __init__(self):
        self.active = False
        self.scale = 1
        self.pos = (0,0)
        self.ref = (0,0)
        self.off = (0,0)

    def start(self, x, y):
        self.active = True
        self.ref = (x,y)

    def update(self, x, y):
        if self.active:
            self.off = tuple((x-y)/self.scale for x,y in zip(self.ref, (x,y)))

    def stop(self):
        self.active = False
        self.pos = self.get_pos()
        self.off = (0,0)

    def get_pos(self):
        result = (x+y for x,y in zip(self.pos, self.off))
        return tuple(x+y for x,y in zip(self.pos, self.off))



class EditWindow:
    def __init__(self):
        self.spinners = []

        self.view = DragController()
        self.view.scale = 2

        self.mpos = (0,0)

        self.area = (0,0,100,100)

        self.selection = None
        self.dirty = False
        self.show_hitboxes = False
        self.show_grid = False
        self.real_size = False
        self.window_scale = 1

        self.loaded_filename = None
        self.foreground = None

    def get_scale(self):
        if self.real_size:
            return self.window_scale
        return self.view.scale

    def save(self, filename):
        result = {
            'spinners': [],
            'view': {
                'pos': self.view.pos,
                'scale': self.view.scale,
                },
            }
#        for spinner in self.spinners:
#            result['spinners'].append(spinner.save())

        for layer, spinners in self.spinner_map.items():
            for eid, spinner in spinners.items():
                result['spinners'].append(spinner.save())

        with open(filename, 'w') as fp:
            json.dump(result, fp)
        self.dirty = False
        self.loaded_filename = filename

    def load(self, filename):
        with open(filename, 'r') as fp:
            data = json.load(fp)

        self.spinners = [Spinner(**x) for x in data['spinners']]

        self.spinner_map = defaultdict(dict)
        for spinner in self.spinners:
            self.spinner_map[spinner.layer][spinner.eid] = spinner

        if self.selection is not None:
            for spinner in self.spinners:
                if spinner.eid == self.selection.eid:
                    self.selection = spinner
                    break
            else:
                self.selection = None


        self.view.pos = data['view']['pos']
        self.view.scale = data['view']['scale']

        self.dirty = False
        self.loaded_filename = filename

    def update_spinners(self, filename):
         with open(filename, 'r') as fp:
            data = json.load(fp)

         new_spinners = {x['eid']: Spinner(**x) for x in data['spinners']}
         for new in new_spinners.values():
            for layer, spinners in self.spinner_map.items():
                if new.eid in spinners.keys():
                    old = spinners[new.eid]
                    old.x = new.x
                    old.y = new.y
                    break
            else:
                self.spinners.append(new)
                self.spinner_map[new.layer][new.eid] = new

    def dirty_check(self):
        print('dirty check')
        with open(self.loaded_filename, 'r') as fp:
            data = json.load(fp)

        new_spinners = [Spinner(**x) for x in data['spinners']]
        if len(new_spinners) != len(self.spinners):
            self.dirty = True
            return

        for new in new_spinners:
            for layer, spinners in self.spinner_map.items():
                if new.eid in spinners.keys():
                    old = spinners[new.eid]
                    if old.neq(new):
                        self.dirty = True
                        return
                    break
            else:
                self.dirty = True
                return


        self.dirty = False

    def screen_to_local(self, pos):
        x,y,w,h = self.area
        xpos, ypos = self.view.get_pos()
        scale = self.get_scale()

        pos = list(pos)
        pos[0] -= x + w/2
        pos[1] -= y + h/2
        pos[0] /= scale
        pos[1] /= scale

        pos[0] += xpos
        pos[1] += ypos

        return pos

    def in_bounds(self, pos):
        x,y,w,h = self.area
        return not( pos[0] < x or pos[0] > x+w or pos[1] < y or pos[1] > y+h)


    def inc_selection_layer(self, amt):
        if self.selection is None:
            return
        old_value = self.selection.layer

        self.selection.layer += amt
        if self.selection.layer < 0:
            self.selection.layer = 0

        if old_value != self.selection.layer:
            self.spinner_map[self.selection.layer][self.selection.eid] = self.selection
            self.spinner_map[old_value].pop(self.selection.eid)

            self.dirty_check()

    def try_select(self, mpos):
        if not self.in_bounds(mpos):
            return

        mpos = self.screen_to_local(mpos)

        options = []
        for spinner in self.spinners:
            dist = spinner.get_hit(*mpos)
            if dist >0:
                options.append((dist, spinner))
        if len(options) == 0:
            self.selection = None
        else:
            self.selection = list(sorted(options, key = lambda x: x[0]))[0][1]

        self.mpos = mpos

    def angle_selection(self, mpos):
        if self.selection is None:
            return
        if not self.in_bounds(mpos):
            return
        spinner = self.selection

        mpos = self.screen_to_local(mpos)
        a = math.atan2(mpos[1]-spinner.y, mpos[0]-spinner.x )
        spinner.a = a

#        self.dirty_check()

    def render(self, screen):
        x,y,w,h = self.area
        xpos, ypos = self.view.get_pos()
        scale = self.get_scale()

        w_real = w/scale
        h_real = h/scale
        target = pygame.Surface((w_real,h_real))
        if self.real_size:
            target.fill((64,64,64))
        else:
            target.fill((64,192,255))

        xpos -= w/(2*scale)
        ypos -= h/(2*scale)

        left = xpos
        top = ypos
        right = left+w_real
        bot = top+h_real

        for layer, spinners in list(self.spinner_map.items())[::-1]:

            for spinner in spinners.values():
                if spinner.x < left-32 or spinner.x > right+32 or spinner.y < top-32 or spinner.y > bot+32:
                    pass
                spinner.render_shape_back(target, xpos, ypos, spinner==self.selection)



            for spinner in spinners.values():
                if spinner.x < left-32 or spinner.x > right+32 or spinner.y < top-32 or spinner.y > bot+32:
                    pass
                spinner.render_shape(target, xpos, ypos, spinner==self.selection, layer)


            if self.show_hitboxes:
                for spinner in spinners.values():
                    if spinner.x < left-32 or spinner.x > right+32 or spinner.y < top-32 or spinner.y > bot+32:
                        pass
                    spinner.render(target, xpos, ypos, spinner==self.selection)

        if False:
            pygame.gfxdraw.pixel(target, int(self.mpos[0]-xpos), int(self.mpos[1]-ypos), (0,255,255))


        #### foreground render
#        1648, 2423

        if self.foreground is not None:
           target.blit(self.foreground, (0,0),
                   pygame.Rect(
                        xpos+1649, ypos+2425,
                        w_real, h_real
                        )
                    )

        if self.selection is not None:
            self.selection.render(target, xpos, ypos, True)
        ### Rescale

        target = pygame.transform.scale_by(target, scale)

        #### Grid Render
        gx, gy = self.screen_to_local((x,y))
        gx = gx-int(gx/8)*8
        gy = gy-int(gy/8)*8

        if self.show_grid or self.real_size:
            if self.real_size:
                c = (0,0,0)
            else:
                c = (128,128,128)
            try:
                for i in range (int(w/scale*8)):
                    pygame.gfxdraw.vline(target,
                        int(i*scale*8-gx*scale),
                        0, int(h),
                        c)
            except: pass
            try:
                for i in range (int(h/scale*8)):
                    pygame.gfxdraw.hline(target,
                        0, int(w),
                        int(i*scale*8-gy*scale),
                        c)
            except: pass

        screen.blit(target, (x, y))

        if self.dirty:
            r = 15
            pygame.gfxdraw.filled_circle(screen, x+r, y+r, r, (255,0,255))

        pass

info = pygame.display.Info()
w = info.current_w
h = info.current_h

edit_window = EditWindow()
edit_window.load(OUTFILE)
Spinner.init()

down_pos = {x:(0,0) for x in (LMB, MMB, RMB)}
monitor_index = 0

foreground = pygame.image.load('foreground.png')
foreground.convert_alpha()
edit_window.foreground = foreground

while True:
    start_time = time.time()

    info = pygame.display.Info()
    w = info.current_w
    h = info.current_h

    screen.fill((255,255,255))

    mpos = pygame.mouse.get_pos()

    edit_window.area = (5,20, w-10, h-30)

    monitors = screeninfo.get_monitors()
    monitor = monitors[monitor_index]
    pxpmm = monitor.width/monitor.width_mm

    grid_size = pxpmm/PXPMM
    edit_window.window_scale = grid_size

    for event in pygame.event.get():
        if event.type == QUIT:
#            edit_window.save(OUTFILE)
            if not edit_window.dirty:
                pygame.quit()
                exit()
        elif event.type == KEYDOWN:
            if event.key == K_s:
                edit_window.save(OUTFILE)
            elif event.key == K_F5:
                edit_window.update_spinners(INFILE)
            elif event.key == K_o:
                edit_window.load(OUTFILE)
            elif event.key == K_b:
                edit_window.show_hitboxes = not edit_window.show_hitboxes
            elif event.key == K_g:
                edit_window.show_grid = not edit_window.show_grid
            elif event.key == K_z:
                edit_window.real_size = not edit_window.real_size
            elif event.key == K_LEFT:
                monitor_index -= 1
                if monitor_index < 0:
                    monitor_index = 0
            elif event.key == K_RIGHT:
                monitor_index += 1
                if monitor_index >= len(monitors):
                    monitor_index = len(monitors)-1
            elif event.key == K_UP:
                edit_window.inc_selection_layer(1)
            elif event.key == K_DOWN:
                edit_window.inc_selection_layer(-1)
        elif event.type == MOUSEBUTTONDOWN:
            down_pos[event.button] = mpos
            if event.button == LMB:
                edit_window.try_select(mpos)
                pass
            elif event.button == MMB:
                edit_window.view.start(*mpos)
                pass
            elif event.button == RMB:
                pass
        elif event.type == MOUSEBUTTONUP:
            if event.button == LMB:
                pass
            elif event.button == MMB:
                edit_window.view.stop()
                pass
            elif event.button == RMB:
                edit_window.dirty_check()
                pass
        elif event.type == MOUSEWHEEL:
            edit_window.view.scale += event.y
            if edit_window.view.scale < 1:
                edit_window.view.scale = 1
            pass

    mouse_state = [0, *pygame.mouse.get_pressed()]

    if mouse_state[RMB]:
        edit_window.angle_selection(mpos)

    edit_window.view.update(*mpos)

#    if mouse_state[RMB]:
#        edit_window.set_drag( -(mpos[0]-down_pos[RMB][0]), -(mpos[1]-down_pos[RMB][1]))


    edit_window.render(screen)

    pygame.display.update()

    stop_time = time.time()
    wait = 0.0167-(stop_time-start_time)
    if wait > 0:
        time.sleep(wait)