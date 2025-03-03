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

#PXPMM = 1.2581913499344692
PXPMM = 1.26

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



    def __init__(self, x, y, a=0, s=8, N=3, eid=0, layer = 0, color='ffffff'):
        self.x = x
        self.y = y
        self.a = a
        self.eid = eid
        self.layer = layer
        self.lonn_color = color

        self.N = N
        #0.83 or 1.16
#        s = 8-0.5*.84*PXPMM
        s = 8
        self.s = s
        self.r = s/math.cos(math.pi/N)

        r = int(self.lonn_color[:2], 16)
        g = int(self.lonn_color[2:4], 16)
        b = int(self.lonn_color[4:6], 16)

        self.enable = True
        self.mode = None
        if b > r and b > g:
            self.mode = 'tri'
        elif b> 200 and r>200 and g> 200:
            self.mode = 'stem'
        else:
            self.enable = False



    def save(self):
        return {
            'x': self.x,
            'y': self.y,
            'a': self.a,
            's': self.s,
            'N': self.N,
            'eid': self.eid,
            'layer': self.layer,
            'color': self.lonn_color,
            }

    def neq(self, a):
        return self.x != a.x or self.y != a.y or self.a != a.a or self.s != a.s or self.N != a.N or self.layer != a.layer or self.eid != a.eid

    def render(self, target, xoff, yoff, selected):
        if not self.enable: return
        x = self.x-xoff
        y = self.y-yoff

        hitbox = Spinner.selected_hitbox if selected else Spinner.hitbox
        target.blit(hitbox, (x-8,y-8))

#        pygame.gfxdraw.pixel(target, int(x),int(y), (0,0,0))

    def get_verts(self, r, x, y):
        verts = []
        N = self.N
        for i in range(N):
            a = self.a+i*2*math.pi/N
            verts.append((
                r*math.cos(a)+x,
                r*math.sin(a)+y
                ))
        return verts


    def render_shape_outline(self, target, xoff, yoff, selected, tracing, scale):
        if not self.enable: return

        if self.mode != 'tri': return

        x = self.x*scale-xoff
        y = self.y*scale-yoff

        r = self.r*scale
        while r > 0:
            verts = self.get_verts(r, x, y)
            r -= 6*scale

            try:
                c = (255,255,255)
                pygame.gfxdraw.aapolygon(target, verts, c)

            except Exception as e:
                print(e)



    def render_shape_back(self, target, xoff, yoff, selected, tracing):
        if not self.enable: return
        if tracing:
            return
        if self.mode != 'tri': return

        x = self.x-xoff
        y = self.y-yoff

        verts = self.get_verts(self.r+1.5, x, y)

        try:
            c = (0,0,0)
            if tracing:
                c = (255,255,255)
            pygame.gfxdraw.aapolygon(target, verts, c)
            pygame.gfxdraw.filled_polygon(target, verts, c)

        except Exception as e:
            print(e)



    def render_shape(self, target, xoff, yoff, selected, layer, tracing):
        if not self.enable: return

        if self.mode != 'tri':
            self.render(target, xoff, yoff, selected)
            return

        x = self.x-xoff
        y = self.y-yoff

        r = self.r-1.5
        if tracing:
            r = self.r

        verts = self.get_verts(self.r-1.5, x, y)

        colors = {0: (255,0,64),
                  1:(255,64,0),
                  }

        try:
            c = colors.get(layer, (255,0,255))
            if tracing:
                c = (128,128,128)
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

    def bump(self, off):
        self.pos = tuple(x+y for x,y in zip(self.pos, off))

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
        self.fg_image_layers = {}
        self.bg_image_layers = {}

        self.marks = []
        self.mark_active = None

        self.tiles_per_grid = 1

    def get_scale(self):
        if self.real_size:
            return self.window_scale/self.tiles_per_grid
        return self.view.scale

    def save(self, filename):
        result = {
            'spinners': [],
            'view': {
                'pos': self.view.pos,
                'scale': self.view.scale,
                },
            'marks': self.marks,
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

        self.marks = data.get('marks', [])

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

        to_remove = []
        for layer, spinners in self.spinner_map.items():
            for eid, old in spinners.items():
                if eid not in new_spinners.keys():
                    to_remove.append((layer, eid, old))

        for layer, eid, old in to_remove:
            print(f'Removed {eid} on update')
            self.spinner_map[layer].pop(eid)
            self.spinners.remove(old)

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

        old_marks = data.get('marks', [])

        if len(self.marks) != len(old_marks):
            self.dirty = True
            return

        for m in self.marks:
            if not m in old_marks:
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

    def local_to_screen(self, pos):
        x,y,w,h = self.area
        xpos, ypos = self.view.get_pos()
        scale = self.get_scale()

        pos = list(pos)

        pos[0] = (pos[0]-xpos)*scale-w/2
        pos[1] = (pos[1]-ypos)*scale-h/2
        return pos


    def in_bounds(self, pos):
        x,y,w,h = self.area
        return not( pos[0] < x or pos[0] > x+w or pos[1] < y or pos[1] > y+h)


    def delete_mark(self):
        if self.mark_active is None:
            return

        self.marks.remove(self.mark_active)
        self.dirty=True

    def start_mark(self, xpos, ypos):
        if self.mark_active is not None:
            return
        xpos, ypos = self.screen_to_local((xpos, ypos))

        for mark in self.marks:
            x,y = mark
            dist = (x-xpos)**2 + (y-ypos)**2
            if dist < 64:
                self.mark_active = mark
                return

        self.mark_active = [xpos, ypos]
        self.marks.append(self.mark_active)

    def stop_mark(self, xpos, ypos):
        if self.mark_active is None:
            return
        xpos, ypos = self.screen_to_local((xpos, ypos))
        self.mark_active[0] = xpos
        self.mark_active[1] = ypos
        self.mark_active = None

    def update_mark(self, xpos, ypos):
        if self.mark_active is None:
            return

        xpos, ypos = self.screen_to_local((xpos, ypos))
        self.mark_active[0] = xpos
        self.mark_active[1] = ypos

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

    def render(self, screen, button_map, rotated, tiles_per_grid):
        x,y,w,h = self.area
        xpos, ypos = self.view.get_pos()
        scale = self.get_scale()

        if rotated:
            x,y,h,w = self.area

        w_real = w/scale
        h_real = h/scale
        target = pygame.Surface((w_real,h_real))
        if self.real_size:
            target.fill((128,128,128))
        else:
            target.fill((64,192,255))

        xpos -= w/(2*scale)
        ypos -= h/(2*scale)

        left = xpos
        top = ypos
        right = left+w_real
        bot = top+h_real

        for name, image_surface in self.bg_image_layers.items():
            if name in button_map.keys() and button_map[name].state:
               target.blit(image_surface, (0,0),
                       pygame.Rect(
                            xpos+1649, ypos+2425,
                            w_real, h_real
                            )
                        )



        for layer, spinners in list(self.spinner_map.items())[::-1]:

            if layer in button_map.keys() and not button_map[layer].state:
                continue

            for spinner in spinners.values():
                if spinner.x < left-32 or spinner.x > right+32 or spinner.y < top-32 or spinner.y > bot+32:
                    pass
                spinner.render_shape_back(target, xpos, ypos, spinner==self.selection, self.real_size)



            for spinner in spinners.values():
                if spinner.x < left-32 or spinner.x > right+32 or spinner.y < top-32 or spinner.y > bot+32:
                    pass
                spinner.render_shape(target, xpos, ypos, spinner==self.selection, layer, self.real_size)


            if self.show_hitboxes:
                for spinner in spinners.values():
                    if spinner.x < left-32 or spinner.x > right+32 or spinner.y < top-32 or spinner.y > bot+32:
                        pass
                    spinner.render(target, xpos, ypos, spinner==self.selection)



        if False:
            pygame.gfxdraw.pixel(target, int(self.mpos[0]-xpos), int(self.mpos[1]-ypos), (0,255,255))




        #### foreground render
#        1648, 2423

        for name, image_surface in self.fg_image_layers.items():
            if name in button_map.keys() and button_map[name].state:
               target.blit(image_surface, (0,0),
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
        def grid_render(n):
            gxb, gyb = self.screen_to_local((x,y))
            gx = gxb-int(gxb/n)*n
            gy = gyb-int(gyb/n)*n


            def get_color(i, g, gb):
                a =round((i*n-g+gb)/n)
                if a%2: return (255,255,255)
                return (64,64,64)

            if self.show_grid or self.real_size:
                if self.real_size:
                    c = (0,0,0)
                    c = (64,64,64)
                else:
                    c = (128,128,128)
                try:
                    for i in range (int(w/scale*n)):
                        pygame.gfxdraw.vline(target,
                            int(i*scale*n-gx*scale),
                            0, int(h),
                            get_color(i, gx, gxb))
                except: pass
                try:
                    for i in range (int(h/scale*n)):
                        pygame.gfxdraw.hline(target,
                            0, int(w),
                            int(i*scale*n-gy*scale),
                            get_color(i,gy, gyb))
                except: pass
        grid_render(4)



        xpos *= scale
        ypos *= scale
        if self.real_size:
            for layer, spinners in list(self.spinner_map.items())[::-1]:

                if layer in button_map.keys() and not button_map[layer].state:
                    continue

                for spinner in spinners.values():
                    if spinner.x < left-32 or spinner.x > right+32 or spinner.y < top-32 or spinner.y > bot+32:
                        pass
                    spinner.render_shape_outline(target, xpos, ypos, spinner==self.selection, self.real_size, scale)

        if 'verge' in button_map.keys() and button_map['verge'].state:
            pygame.gfxdraw.box(target, pygame.Rect(0, 9*8*scale-ypos, w, 16*scale), (0,0,0))
            pygame.gfxdraw.hline(target, 0, int(w), int(9*8*scale-ypos), (255,255,255))
            pygame.gfxdraw.hline(target, 0, int(w), int(11*8*scale-ypos), (255,255,255))

        for mark in self.marks:
            color = (255,255,0)
            if mark is self.mark_active:
                color= (255,0,255)

            r = 4*scale
            mx = round(mark[0]*scale - xpos)
            my = round(mark[1]*scale - ypos)
            pygame.gfxdraw.aacircle(target, mx, my, round(r), color)
            r = round(r*0.707)
            pygame.gfxdraw.line(target, mx-r, my-r, mx+r, my+r, color)
            pygame.gfxdraw.line(target, mx+r, my-r, mx-r, my+r, color)


        if rotated:
            target = pygame.transform.rotate(target, 90)

        screen.blit(target, (x, y))

        if self.dirty:
            r = 15
            pygame.gfxdraw.filled_circle(screen, x+r, y+r, r, (255,0,255))

        pass

class Button():
    def __init__(self, x, y, w, h, state, name):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.state = state
        self.name = name

        self.xoff = 0
        self.yoff = 0

    def toggle(self, mpos = None):
        if mpos is None:
            self.state = not self.state
            return

        x = self.xoff+self.x
        y = self.yoff+self.y
        w = self.w
        h = self.h

        if mpos[0] < x or mpos[0] > x+w or mpos[1] < y or mpos[1] > y+h:
            return
        self.state = not self.state

    def render(self, screen):
        x = self.xoff+self.x
        y = self.yoff+self.y
        w = self.w
        h = self.h

        bg = (255,128,128)
        if self.state:
            bg = (128,255,255)

        pygame.gfxdraw.box(screen, pygame.Rect(x,y,w,h), bg)
        pygame.gfxdraw.rectangle(screen, pygame.Rect(x,y,w,h), (0,0,0))
        label = str(self.name)
        fs = font.render(label, True, (0,0,0))
        fw,fh = fs.get_size()
        screen.blit(fs, (x+(w-fw)/2, y+(h-fh)/2))


info = pygame.display.Info()
w = info.current_w
h = info.current_h

edit_window = EditWindow()
edit_window.load(OUTFILE)
Spinner.init()

down_pos = {x:(0,0) for x in (LMB, MMB, RMB)}
monitor_index = 0

fg_image_layers = {}
bg_image_layers = {}

foreground = pygame.image.load('foreground.png')
foreground.convert_alpha()
fg_image_layers['foreground'] = foreground

foreground = pygame.image.load('background_decals.png')
foreground.convert_alpha()
bg_image_layers['bg decals'] = foreground



edit_window.fg_image_layers = fg_image_layers
edit_window.bg_image_layers = bg_image_layers

controls_width = 100


buttons = []

buttons.extend([
Button(0, 25*i, controls_width, 20, True, x) for i,x in enumerate(fg_image_layers.keys())
])

yoff = len(buttons)
render_layers = [0, 1, 2, 'verge']
buttons.extend([
Button(0, 25*(i+yoff), controls_width, 20, True, x) for i,x in enumerate(render_layers)
])

yoff = len(buttons)
buttons.extend([
Button(0, 25*(i+yoff), controls_width, 20, True, x) for i,x in enumerate(bg_image_layers.keys())
])

button_map = {x.name: x for x in buttons}

layer_toggle_map = {
    K_1: 0,
    K_2: 1,
    K_3: 2,
    K_4: 'verge',
}

rotated = False
tiles_per_grid = 1

while True:
    start_time = time.time()

    info = pygame.display.Info()
    w = info.current_w
    h = info.current_h

    screen.fill((255,255,255))

    mpos = pygame.mouse.get_pos()


    controls_area = (w-controls_width-5, 20, controls_width, h-25)

    edit_window.area = (5,20, w-15-controls_width, h-25)

    monitors = screeninfo.get_monitors()
    monitor = monitors[monitor_index]
    pxpmm = monitor.width/monitor.width_mm

    grid_size = pxpmm/PXPMM
    edit_window.window_scale = grid_size

    for button in buttons:
        button.xoff = controls_area[0]
        button.yoff = controls_area[1]

    for event in pygame.event.get():
        if event.type == QUIT:
#            edit_window.save(OUTFILE)
            if not edit_window.dirty:
                pygame.quit()
                exit()
        elif event.type == KEYDOWN:
            if event.key in layer_toggle_map.keys():
                button_map[layer_toggle_map[event.key]].toggle()
            elif event.key == K_DELETE:
                edit_window.delete_mark()
            elif event.key == K_BACKQUOTE:
                for k in fg_image_layers.keys():
                    button_map[k].toggle()
                for k in bg_image_layers.keys():
                    button_map[k].toggle()
            elif event.key == K_r:
                rotated = not rotated
            elif event.key == K_SPACE:
                edit_window.tiles_per_grid = 3-edit_window.tiles_per_grid
            elif event.key == K_s:
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
            elif event.key == K_u:
                edit_window.view.bump((0,1))
            elif event.key == K_h:
                edit_window.view.bump((1,0))
            elif event.key == K_j:
                edit_window.view.bump((0,-1))
            elif event.key == K_k:
                edit_window.view.bump((-1,0))
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
                for button in buttons:
                    button.toggle(mpos)
                pass
            elif event.button == MMB:
                edit_window.view.start(*mpos)
                pass
            elif event.button == RMB:
                edit_window.start_mark(*mpos)
                pass
        elif event.type == MOUSEBUTTONUP:
            if event.button == LMB:
                pass
            elif event.button == MMB:
                edit_window.view.stop()
                pass
            elif event.button == RMB:
                edit_window.stop_mark(*mpos)
                edit_window.dirty_check()
                pass
        elif event.type == MOUSEWHEEL:
            edit_window.view.scale += event.y
            if edit_window.view.scale < 1:
                edit_window.view.scale = 1
            pass

    edit_window.update_mark(*mpos)

    mouse_state = [0, *pygame.mouse.get_pressed()]

    if mouse_state[RMB]:
        edit_window.angle_selection(mpos)

    edit_window.view.update(*mpos)

#    if mouse_state[RMB]:
#        edit_window.set_drag( -(mpos[0]-down_pos[RMB][0]), -(mpos[1]-down_pos[RMB][1]))


    edit_window.render(screen, button_map, rotated, tiles_per_grid)

    for button in buttons:
        button.render(screen)

    pygame.display.update()

    stop_time = time.time()
    wait = 0.0167-(stop_time-start_time)
    if wait > 0:
        time.sleep(wait)
