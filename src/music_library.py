from tkinter import *
from json import load, JSONEncoder
from functools import partial

from library.library import Library
from ui.ui import Editor, StatusBar, Tree, LibraryListener, Task

config_path = "config.json"

with open(config_path) as config_file:
    print("Reading application configuration from {}".format(config_path))
    config = load(config_file)


class ConfigEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, BooleanVar):
            return o.get()
        return super().default(o)


class WindowTitle(LibraryListener):
    def __init__(self, root):
        self.root = root

    def on_library_change(self, library):
        self.root.title("{} - {}".format(config['window-title'], library.library_name))


class MusicLibrary:
    def __init__(self):
        super().__init__()
        self.selected_library = None
        self.library = None
        self.__make_widgets()
        self.__make_bindings()
        self.__make_menu()
        self.tree.tree.pack(expand=Y, side=LEFT, fill=BOTH)
        self.editor.pack(expand=Y, side=RIGHT, fill=BOTH)
        self.status_bar.label.pack(side=BOTTOM, fill=X)
        self.library_listeners = [self.tree, self.editor, WindowTitle(self.root)]
        self.__change_library(next(lib for lib in config['libraries'] if lib['selected'].get()))
        self.root.protocol("WM_DELETE_WINDOW", self.__on_exit)
        self.root.mainloop()

    def __make_widgets(self):
        root = Tk()
        root.state('zoomed')
        self.status_bar = StatusBar(root)
        self.editor = Editor(config['editor'], self.status_bar, root)
        self.tree = Tree(config['tree'], root)
        self.root = root

    def __save_command(self):
        return self.make_task(self.editor.save, task_name=lambda event=None: "Saving tags in {} files"
                              .format(len(self.editor.tracks)))

    def __reload_command(self):
        return self.make_task(self.__on_reload, task_name=lambda event=None, selection=None: "Reloading {}".format(
            selection or self.tree.selected_node))

    def __make_bindings(self):
        self.tree.tree.bind("<F5>", self.__reload_command())

        self.tree.tree.bind("<<TreeviewSelect>>", self.make_task(self.__on_node_selected))
        self.root.bind("<Control-s>", self.__save_command())

    def rename_command(self):
        # from os import rename
        self.library.rename(self.editor.tracks, self.selected_library['path'])
            # path = track['PATH']
            # composer = track['COMPOSER']
            # genre = track['GEN']

    def __make_menu(self):
        self.menu = Menu(self.root)
        self.root.config(menu=self.menu)
        file_menu = Menu(self.menu)
        self.menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save tags", command=self.__save_command())
        file_menu.add_command(label="Reload", command=self.__reload_command())
        file_menu.add_command(label="Rename", command=self.rename_command)
        library_menu = Menu(self.menu)

        self.menu.add_cascade(label="Library", menu=library_menu)
        library_menu.add_command(label="Rescan",
                                 command=self.make_task(self.__rescan_library))
        open_library_menu = Menu(library_menu)
        library_menu.add_cascade(label="Open", menu=open_library_menu)
        for lib in config['libraries']:
            lib['selected'] = BooleanVar(value=lib.get('selected', False))
            open_library_menu.add_checkbutton(label=lib['name'], variable=lib['selected'],
                                              command=self.make_task(self.__change_library,
                                              lambda new_library: "Opening library {}".format(
                                                  new_library['name']), lib))
        library_menu.add_command(label="New...", command=self.__new_library)

    def make_task(self, function, task_name=None, *args):
        task = Task(function, self.status_bar, task_name)
        return partial(task.run, *args)

    def __on_exit(self):
        print("About to close window: saving application configuration")
        from json import dump
        with open(config_path, 'w') as config_file:
            dump(config, config_file, cls=ConfigEncoder, sort_keys=True, indent=4)
        self.root.destroy()

    def __on_reload(self, event=None, selection=None):
        selected_node = selection or self.tree.selected_node
        if selected_node:
            self.tree.delete_children(selected_node)
            self.tree.fetch_children(selected_node)
            self.__on_node_selected(event, selected_node)

    def __change_library(self, new_library):
        if self.selected_library:
            self.selected_library['selected'].set(False)
        self.selected_library = new_library
        self.selected_library['selected'].set(True)
        self.library = Library(self.selected_library['name']).restore()
        for listener in self.library_listeners:
            listener.on_library_change(self.library)

    def __new_library(self):
        dialog = Toplevel(self.root)
        Label(dialog, anchor=W, width=20, pady=5, justify=LEFT, text="Library name: ").grid(row=0, column=0)
        library_name = Entry(dialog, width=50)
        Label(dialog, anchor=W, width=20, pady=5, justify=LEFT, text="Library path: ").grid(row=1, column=0)
        library_path = Entry(dialog, width=50)
        library_name.grid(row=0, column=1)
        library_path.grid(row=1, column=1)

        def create_library():
            name = library_name.get()
            path = library_path.get()
            print("Creating Library {} at {}".format(name, path))
            new_library = {
                "name": name,
                "path": path,
                "selected": BooleanVar(False)
            }
            dialog.destroy()
            config['libraries'].append(new_library)
            self.library = Library(new_library['name']).create(new_library['path'], self.status_bar)
            self.__change_library(new_library)

        Button(dialog, text="OK", command=self.make_task(create_library), width=10, pady=5).grid(row=2, column=0,
                                                                                                 columnspan=3)
        dialog.grab_set()
        self.root.wait_window(dialog)

    def __rescan_library(self):
        self.library = self.library.create(self.selected_library['path'], self.status_bar)
        for listener in self.library_listeners:
            listener.on_library_change(self.library)

    def __on_node_selected(self, event=None, selection=None):
        selection = selection or self.tree.selected_node
        children = self.tree.children(selection)
        for child in children:
            self.tree.fetch_children(child)
        self.editor.select(selection)


MusicLibrary()
