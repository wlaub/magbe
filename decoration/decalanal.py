import sys, os
import time
import json

from collections import defaultdict

import tabulate

import watchdog.events
import watchdog.observers

filename = '/home/wlaub/celeste/olympus/decal_dump.txt'


class Decal():
    def __init__(self, line):
        self.line = line

        parts = line.split(' ')

        self.layer = parts[0]
        self.path = parts[1]
        self.room = ' '.join(parts[2:])

    def get_key(self):

        name = self.path.split('/')[-1]
        base = '/'.join(self.path.split('/')[:-1])

        if 'iambad/magbe/mush/' in self.path:
            parts = name.split('.')
            parts.pop(2)
            name = '.'.join(parts)
        elif 'iambad/magbe/gill/' in self.path:
            if name[0] != 'h':
                parts = name.split('.')
                parts.pop(2)
                name = '.'.join(parts)
        elif 'iambad/magbe/stem/' in self.path:
            if name[0] != 'h':
                try:
                    parts = name.split('.')
                    parts.pop(3)
                    name = '.'.join(parts)
                except:
                    pass
#        elif 'iambad/magbe/tri/s' in self.path and name[0]=='s':
#            parts = name[1:].split('.')
#            return int(parts[0])%2*3+int(parts[1])
#            return (int(parts[0])%2)*3#+int(parts[1])

        return base+'/'+name



    def get_color(self):
        name = self.path.split('/')[-1]
        if 'iambad/magbe/mush/' in self.path:
            return int(name.split('.')[2])

        if 'iambad/magbe/gill/' in self.path:
            if name[0] == 'h': return None

            return int(name.split('.')[2])

        if 'iambad/magbe/stem/' in self.path:
            if name[0] == 'h': return None

            try:
                return int(name.split('.')[3])
            except:
                return None



        if 'iambad/magbe/tri/s' in self.path and name[0]=='s':
            parts = name[1:].split('.')
            return int(parts[0])%2*3+int(parts[1])
            return (int(parts[0])%2)*3#+int(parts[1])

        return None


class DecalMachine():
    def __init__(self, filename):
        self.filename = filename

        self.load()

    def load(self):
        with open(self.filename, 'r') as fp:
            raw=fp.read().strip()

        self.decals = []
        for line in raw.split('\n'):
            try:
                self.decals.append(Decal(line))
            except Exception as e:
#                print(f'Failed on {line} with {e}')
                pass

    def get_global_counts(self, filter_text):
        counts = defaultdict(lambda: 0)
        room_counts = defaultdict(lambda: 0)

        if filter_text is None:
            filter_text = self.filter_buffer.document.text
        room_name = self.room_buffer.document.text

        for decal in self.decals:
            path = decal.get_key()
            if path.startswith(filter_text):
                counts[path[len(filter_text):]] += 1
                if decal.room == room_name:
                    room_counts[path[len(filter_text):]] += 1

        return self.format_counts(counts, room_counts)

    def get_room_counts(self, filter_text, room_name):
        counts = defaultdict(lambda: 0)

        if filter_text is None:
            filter_text = self.filter_buffer.document.text
        if room_name is None:
            room_name = self.room_buffer.document.text

        for decal in self.decals:
            path = decal.get_key()
            if decal.room == room_name and decal.path.startswith(filter_text):
                counts[decal.path[len(filter_text):]] += 1

        return self.format_counts(counts)

    def format_counts(self, counts, room_counts = None):

        if room_counts is None:
            rows = [(v, k) for k,v in counts.items()]
        else:
            rows = [(v, room_counts[k], k) for k,v in counts.items()]

        rows = sorted(rows)
        return tabulate.tabulate(rows, tablefmt='plain')


    def count_colors(self):
        counts = defaultdict(lambda: 0)

        filter_text = self.filter_buffer.document.text
        for decal in self.decals:
            if decal.path.startswith(filter_text):
                color = decal.get_color()
                if color is not None:
                    counts[color] += 1

        return self.format_color_counts(counts)


    def count_room_colors(self):
        counts = defaultdict(lambda: 0)

        filter_text = self.filter_buffer.document.text
        room_name = self.room_buffer.document.text

        for decal in self.decals:
            if decal.room == room_name and decal.path.startswith(filter_text):
                color = decal.get_color()
                if color is not None:
                    counts[color] += 1

        return self.format_color_counts(counts)


    def format_color_counts(self, counts):
        if len(counts) == 0: return ''

        top = ''
        bot = ''
        for i in range(max(counts.keys())+1):
            top += f'{i:02} '
            bot += f'{counts[i]:02} '

        return top+'\n'+bot


dm = DecalMachine(filename)


from prompt_toolkit import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout import ScrollablePane
from prompt_toolkit.layout.containers import VSplit, HSplit, Window
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.widgets import Label, VerticalLine, HorizontalLine
from prompt_toolkit.document import Document
from prompt_toolkit.key_binding import KeyBindings

kb = KeyBindings()
@kb.add('c-q')
def exit_(event):
    event.app.exit()
@kb.add('c-c')
def exit_(event):
    event.app.exit()



def update_lists(buffer):
    global_list.text=dm.get_global_counts(None)
    room_list.text=dm.get_room_counts(None, None)

    global_color_counts.text = dm.count_colors()
    room_color_counts.text = dm.count_room_colors()

def update_room_list(buffer):
    room_list.text=dm.get_room_counts(None, None)
    room_color_counts.text = dm.count_room_colors()

global_list = FormattedTextControl()
room_list = FormattedTextControl()
global_color_counts = FormattedTextControl()
room_color_counts = FormattedTextControl()


filter_buffer = Buffer(on_text_changed=update_lists, multiline=False)
room_buffer = Buffer(on_text_changed=update_lists, multiline=False)

dm.filter_buffer = filter_buffer
dm.room_buffer = room_buffer

filter_buffer.set_document(Document('decals/iambad/magbe/'))


root_container = HSplit([
    VSplit([
        Label('Filter:', dont_extend_width=True),
        Window(content=BufferControl(buffer=filter_buffer, focus_on_click=True), height=1),
        VerticalLine(),
        Label('Room:', dont_extend_width=True),
        Window(content=BufferControl(buffer=room_buffer, focus_on_click = True)),
        ]),
    HorizontalLine(),
    VSplit([
        Window(content=global_color_counts, height=2),
        VerticalLine(),
        Window(content=room_color_counts, height=2),
        ]),
    HorizontalLine(),
    VSplit([
        ScrollablePane(content=Window(content=global_list)),
        VerticalLine(),
        ScrollablePane(content=Window(content=room_list)),
        ]),
])
layout = Layout(root_container)

@kb.add('f5')
def refresh_(event):
    dm.load()
    update_lists(None)

class MyEventHandler(watchdog.events.FileSystemEventHandler):
    def on_closed(self, event):
        dm.load()
        update_lists(None)

#event_handler = MyEventHandler()
#observer = watchdog.observers.Observer()
#observer.schedule(event_handler, dm.filename)

#observer.start()

app = Application(layout=layout, full_screen=True, key_bindings=kb, mouse_support=True)
app.run()

#observer.stop()
#observer.join()

