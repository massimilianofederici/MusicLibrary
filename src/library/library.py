from tags.tagreader import TagReader
from tags.tagreader import NullListener
from pymongo import MongoClient
from tags.tagwriter import TagWriter

SEARCH_TEMPLATE = {
    'TITLE': True,
    'TRACKNUMBER': True,
}


class Library:
    def __init__(self, library_name):
        self.library_name = library_name
        self.client = MongoClient()
        self.collection = {}
        self.tag_reader = TagReader()
        self.tag_writer = TagWriter()

    def restore(self):
        db = self.client[self.library_name]
        self.collection = db.tags
        return self

    def create(self, folder_name, listener=NullListener()):
        db = self.client[self.library_name]
        db.drop_collection('tags')
        self.collection = db.tags
        documents = self.tag_reader.readfolder(folder_name, listener).items()
        for key, tag in documents:
            self.collection.insert_one(tag)
        return self

    def track_details(self, track_id):
        return self.collection.find_one({'_id': track_id})

    def load_single_picture(self, track):
        return self.tag_reader.read_pictures(track['PATH'])[0]

    def replace_cover_art(self, raw_data, track):
        print("Saving cover art in {}".format(track['PATH']))
        self.tag_writer.replace_picture(raw_data, track['PATH'])

    def view(self):
        return LibraryView(self.collection)

    def aggregate(self, match, group_by):
        if group_by == 'TITLE':
            return [track['TITLE'] for track in self.find_tracks(match)]
        pipeline = [
            {"$match": match},
            {"$group": {"_id": "$" + group_by}}
        ]
        cur = self.collection.aggregate(pipeline)
        return sorted([item['_id'] for item in cur])

    def find_tracks(self, match):
        return list(self.collection.find(match).sort('TRACKNUMBER'))

    def store(self, track_id, tags):
        file_name = tags['PATH']
        self.collection.replace_one({'_id': track_id}, tags)
        self.tag_writer.write(tags, file_name)

    def rename(self, tracks, base_folder):
        for track in tracks:
            composer = track['COMPOSER']
            genre = track['GENRE']
            album = track['ALBUM']
            artist = track['ARTIST']
            year = track['DATE']
            track_number = track['TRACKNUMBER']
            new_folder = "{}\\{}\\{}\\{}\\{}, {}".format(base_folder, composer, genre, album, artist, year)
            import os
            os.makedirs(new_folder, exist_ok=True)
            new_path = "{}\\{}.flac".format(new_folder, track_number.zfill(2))
            # print(new_path)
            existing_path = track['PATH']
            print(existing_path)
            if new_path != existing_path:
            # from shutil import rename
                import shutil
                shutil.move(existing_path, new_path)

    def __str__(self, *args, **kwargs):
        return "Library {}".format(self.library_name)


class LibraryView:
    def __init__(self, collection):
        self.collection = collection
        self.expressions = []

    def by(self, expression):
        self.expressions.append(expression)
        return self

    def filter(self):
        self.by('TITLE')
        return LibraryFilter(self.expressions, self.collection)


class LibraryFilter:
    def __init__(self, expressions, collection):
        self.current_expression = -1
        self.expressions = expressions
        self.collection = collection
        self.match = {}
        self.ids = self.__aggregate()

    def current_view(self):
        return self.expressions[self.current_expression]

    def using(self, value):
        self.match[self.current_view()] = value
        self.ids = self.__aggregate()
        return self

    def remove_current_filter(self):
        prev_view = self.expressions[self.current_expression - 1]
        self.current_expression -= 2
        del self.match[prev_view]
        self.ids = self.__aggregate()

    def reset(self):
        self.current_expression = -1
        self.match = {}
        self.ids = self.__aggregate()

    def __aggregate(self):
        self.current_expression += 1
        pipeline = [
            {"$match": self.match},
            {"$group": {"_id": "$" + self.current_view()}}
        ]
        if self.current_view() == 'TITLE':
            return list(self.collection.find(self.match, SEARCH_TEMPLATE).sort('TRACKNUMBER'))

        cur = self.collection.aggregate(pipeline)
        return sorted([item['_id'] for item in cur])
