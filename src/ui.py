__author__ = 'Massimiliano'

from library.library import Library
from tags.tagreader import TagReaderListener
from ui.ProgressText import ProgressText
from prompt_toolkit.shortcuts import get_input
from prompt_toolkit.contrib.completers import WordCompleter

# folder_name = get_input('Library Path: ')
folder_name = "C:\\Users\\Massimiliano\\Music"

actions = ["Edit"]


def format_song(song):
        return "{} - {}".format(song['TRACKNUMBER'], song['TITLE'])


class Listener(TagReaderListener):
    number_of_files = 0
    index = 0;

    def file_error(self, file):
        pass

    def read_start(self, count):
        self.number_of_files = count
        print("Found {} files".format(self.number_of_files))
        self.progress = ProgressText(count)

    def file_read(self, filename):
        self.index += 1
        # self.progress.on_progress()

    def read_complete(self):
        print("")


class Ui:

    def __init__(self):
        super().__init__()
        self.library = Library('music').create(folder_name, Listener())
        views = ['COMPOSER', 'GENRE', 'ALBUM', 'ARTIST']
        library_view = self.library.view()
        for view in views:
            self.filters = library_view.by(view)
        self.filters = self.filters.filter()
        self.track_selection = False

    def prompt(self, items):
        from prompt_toolkit.key_binding.manager import KeyBindingManager
        from prompt_toolkit.keys import Keys
        key_binding_manager = KeyBindingManager()

        @key_binding_manager.registry.add_binding(Keys.F4)
        def _(event):
            self.filters.remove_current_filter()
            self.run()

        @key_binding_manager.registry.add_binding(Keys.F1)
        def _(event):
            if self.filters.current_view() != 'TITLE':
                first_item = self.filters.ids[0]
                event.cli.current_buffer.insert_text(first_item)

        return get_input('> ', completer=WordCompleter(items, ignore_case=True),
                         key_bindings_registry=key_binding_manager.registry,
                         display_completions_in_columns=True)

    def handle_track_selection(self):
        songs = [format_song(song) for (song) in self.filters.ids]
        for song in songs:
            print(song)
        title = self.prompt(songs)
        index = songs.index(title)
        song = self.filters.ids[index]
        track_details = self.library.track_details(song['_id'])
        from bson.json_util import dumps
        print(dumps(track_details))
        self.track_selection = True

    def get_selection(self):
        if self.track_selection:
            for action in actions:
                print(action)
            self.prompt(actions)
        else:
            if self.filters.current_view() == 'TITLE':
                self.handle_track_selection()
            else:
                for item in self.filters.ids:
                    print(item)
                selection = self.prompt(self.filters.ids)
                self.filters.using(selection)
                self.track_selection = False

    def run(self):
        while True:
            self.get_selection()

Ui().run()
