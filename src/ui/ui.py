__author__ = 'Massimiliano'

from abc import abstractmethod
from tkinter.ttk import Frame
from tkinter.ttk import Label
from tkinter.ttk import Combobox
from tkinter.ttk import Treeview
from tkinter.ttk import Button
from tkinter import W
from io import BytesIO
from copy import copy
from ast import literal_eval
from tkinter import IntVar
from tkinter.ttk import Radiobutton

from PIL.ImageTk import PhotoImage
from PIL import Image

from tags.tagreader import TagReaderListener
from library.library import Library
from ui.modal import ModalDialog


class LibraryListener:
    @abstractmethod
    def on_library_change(self, library: Library):
        pass


class StatusBar(TagReaderListener):
    def __init__(self, master):
        super().__init__()
        self.label = Label(master, text='', anchor=W)
        self.label.pack()
        self.index = 0
        self.expected_count = 0

    def start_task(self, text):
        self.label['text'] = text + "..."

    def task_complete(self):
        self.label['text'] += 'Done'

    def read_complete(self, elapsed_time):
        self.set("{} files read in {} milliseconds".format(self.expected_count, round(elapsed_time, 2)))

    def read_start(self, count):
        self.expected_count = count
        self.index = 0
        self.set("Reading tags in {} files".format(self.expected_count))

    def file_read(self, file):
        self.index += 1
        percent = round(100 * self.index / self.expected_count, 2)
        self.set("Reading tags in {} files: {}%".format(self.expected_count, percent))

    def counting_files(self):
        self.set("Counting files...")

    def set(self, text: str):
        self.label['text'] = text


class Task:
    def __init__(self, function, status_bar: StatusBar, task_name=None):
        super().__init__()
        self.task_name = task_name
        self.function = function
        self.status_bar = status_bar

    def __wrap(self, *args):
        if self.task_name:
            self.status_bar.start_task(self.task_name(*args))
            print(self.task_name(*args))
        self.function(*args)
        if self.task_name:
            self.status_bar.task_complete()

    def run(self, *args):
        from threading import Thread
        from functools import partial
        thread = Thread(target=partial(self.__wrap, *args))
        thread.start()


class Tree(LibraryListener):
    def __init__(self, config, master):
        self.views = config['views']
        self.library = None
        self.__make_widgets(master)

    def __make_widgets(self, root):
        self.tree = Treeview(root)

    def on_library_change(self, library):
        self.library = library
        self.__make_root_nodes()

    def __make_root_nodes(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        root_nodes = self.query_library({}, self.views[0])
        for node in root_nodes:
            child = self.tree.insert("", "end", self.__make_node_id(None, self.views[0], node), text=node,
                                     tags=self.views[0])
            self.fetch_children(child)

    @staticmethod
    def __make_node_id(parent_node, node_type, node_value):
        node_id = {}
        if parent_node:
            node_id = copy(parent_node)
        node_id[node_type] = node_value
        return node_id

    def can_be_expanded(self, node_type):
        return node_type != self.views[len(self.views) - 1]

    def get_child_node_type(self, node_type):
        return self.views[self.views.index(node_type) + 1]

    def query_library(self, node_id, view):
        return self.library.aggregate(node_id, view)

    def __has_children(self, node):
        return len(self.children(node)) > 0

    def fetch_children(self, node):
        if not self.__has_children(node):
            node_type = self.tree.item(node, "tags")[0]
            if self.can_be_expanded(node_type):
                children_node_type = self.get_child_node_type(node_type)
                node_id = literal_eval(node)
                nodes = self.query_library(node_id, children_node_type)
                for child_node in nodes:
                    self.tree.insert(node, "end", self.__make_node_id(node_id, children_node_type, child_node),
                                     text=child_node, tags=children_node_type)

    def delete_children(self, parent_node):
        children = self.children(parent_node)
        for node in children:
            self.tree.delete(node)

    @property
    def selected_node(self):
        if len(self.tree.selection()):
            return self.tree.selection()[0]

    def children(self, node):
        return self.tree.get_children(node)


class Editor(Frame, LibraryListener):
    def __init__(self, config: dict, status_bar: StatusBar, master=None, **kw):
        super().__init__(master, **kw)
        self.editor_fields = config['fields']
        self.multi_value = config['multi-value']
        self.status_bar = status_bar
        self.library = None
        self.widgets = self.__make_widgets()
        self.tracks = []
        self.current_selection = None

    def __make_widgets(self):
        widgets = {}
        for index, editor_field in enumerate(self.editor_fields):
            label = Label(self, width=50, padding=5, text=editor_field.title())
            combo = Combobox(self, width=100)
            widgets[editor_field] = {}
            widgets[editor_field]['label'] = label
            widgets[editor_field]['widget'] = combo
            label.grid(row=index, column=0)
            combo.grid(row=index, column=1)
        index += 1
        label = Label(self, width=50, padding=5, text="Pictures")
        button = Button(self, text="...", command=self.__load_pictures)
        label.grid(row=index, column=0)
        button.grid(row=index, column=1)
        return widgets

    @staticmethod
    def __make_picture(raw_data, index):
        raw_image = Image.open(BytesIO(raw_data)).resize((150, 150), Image.ANTIALIAS)
        tk_image = PhotoImage(raw_image)
        row = int(index / 4)
        column = int(index % 4)

        def __make_radio(dialog, v):
            radio = Radiobutton(dialog, image=tk_image, variable=v, value=index)
            radio.grid(row=row, column=column)
            return radio
        return {
            "raw_data": raw_data,
            "tk_image": tk_image,
            "make_radio": __make_radio
        }

    def __load_pictures(self):
        if self.tracks:
            self.__pictures = []
            all_pictures = {}
            for track in self.tracks:
                all_pictures[track['_id']] = self.library.load_single_picture(track).data
            v = IntVar(0)

            def __make_pictures_widgets(dialog):
                for index, picture_data in enumerate(set([data for data in all_pictures.values()])):
                    picture = self.__make_picture(picture_data, index)
                    self.__pictures.append(picture)
                    picture['make_radio'](dialog, v)

                index += 1
                with open("empty.gif", "rb") as f:
                    empty_image = self.__make_picture(f.read(), index)
                    self.__pictures.append(empty_image)
                    empty_image['make_radio'](dialog, v)
                    self.new_image_button = empty_image['make_radio'](dialog, v)
                    self.new_image_button.bind("<Double-Button-1>", __load_cover_art_from_filesystem)

            def __load_cover_art_from_filesystem(event):
                from tkinter.filedialog import LoadFileDialog
                d = LoadFileDialog(self.new_image_button.master)
                file_name = d.go("c:/", "*.jpg")
                if file_name:
                    with open(file_name, "rb") as f:
                        empty_image = self.__make_picture(f.read(), len(self.__pictures) - 1)
                        self.__pictures.remove(self.__pictures[len(self.__pictures) - 1])
                        self.__pictures.append(empty_image)
                        self.new_image_button['image'] = empty_image['tk_image']

            result = ModalDialog.open(self, __make_pictures_widgets, lambda: self.__pictures[v.get()]['raw_data'],
                                      "Covert Art")
            if result:
                [self.library.replace_cover_art(result, track) for track in self.tracks if
                 all_pictures[track['_id']] != result]

    def select(self, selected_node):
        if self.current_selection != selected_node:
            self.current_selection = selected_node
            selected_node_id = literal_eval(selected_node)
            self.tracks = self.library.find_tracks(selected_node_id)
            for field in self.editor_fields:
                self.__set_combo_value(field)
            self.status_bar.set("{} matching tracks".format(len(self.tracks)))

    def save(self, event=None):
        for track in self.tracks:
            for editor_field in self.editor_fields:
                if self.__is_changed(track, editor_field):
                    track[editor_field] = self.widgets[editor_field]['widget'].get()
                    self.library.store(track['_id'], track)

    def __set_combo_value(self, field: str):
        combo_value = sorted(list(set([track.get(field, '') for track in self.tracks])))
        widget = self.widgets[field]
        combo = widget['widget']
        combo['values'] = combo_value
        combo.delete(0, "end")
        initial_value = self.multi_value
        if len(combo_value) == 1:
            initial_value = combo_value[0]
        combo.insert(0, initial_value)

    def __is_changed(self, track: dict, editor_field: str):
        tag_value = self.widgets[editor_field]['widget'].get()
        initial_value = track.get(editor_field) or ''
        return tag_value != initial_value and tag_value != self.multi_value

    def on_library_change(self, library: Library):
        self.library = library
        self.tracks = []
        self.current_selection = None
        for field in self.editor_fields:
            widget = self.widgets[field]
            combo = widget['widget']
            combo['values'] = []
            combo.delete(0, "end")
