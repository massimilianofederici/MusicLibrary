from tags.tagreader import TagReader
from pymongo import MongoClient

SEARCH_TEMPLATE = {
    'TITLE': True,
    'TRACKNUMBER': True,
}


class Library:
    def __init__(self, library_name):
        self.library_name = library_name
        self.client = MongoClient()
        self.collection = {}

    def create(self, folder_name):
        db = self.client[self.library_name]
        db.drop_collection('tags')
        self.collection = db.tags
        documents = TagReader().readfolder(folder_name).items()
        for key, tag in documents:
            self.collection.insert_one(tag)
        return self

    def view_tracks_by_album(self, album):
        return list(self.collection.find({'ALBUM': album}, SEARCH_TEMPLATE).sort('TRACKNUMBER'))

    def track_details(self, track_id):
        return self.collection.find_one({'_id': track_id})

    def view(self):
        return LibraryView(self.collection)


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
        self.expressions = expressions
        self.collection = collection
        self.match = {}
        self.ids = self.__aggregate()

    def using(self, value):
        filter_expression = self.expressions.pop(0)
        self.match[filter_expression] = value
        self.ids = self.__aggregate()
        return self

    def __aggregate(self):
        display = self.expressions[0]
        pipeline = [
            {"$match": self.match},
            {"$group": {"_id": "$" + display}}
        ]
        cur = self.collection.aggregate(pipeline)
        return [item['_id'] for item in cur]
