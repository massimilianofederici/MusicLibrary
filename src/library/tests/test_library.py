__author__ = 'Massimiliano'

import unittest
import fnmatch
import os
from library.library import Library


class TestLibrary(unittest.TestCase):

    def setUp(self):
        self.library_name = 'TestLibrary'
        self.folder_name = '.'
        from pymongo import MongoClient
        self.client = MongoClient()
        self.client.drop_database(self.library_name)

    def test_should_save_library_state(self):
        fullpath = os.path.abspath(self.folder_name)
        matches = []
        for root, dirnames, filenames in os.walk(self.folder_name):
            for filename in fnmatch.filter(filenames, "*.flac"):
                matches.append(os.path.join(root, filename))
        count = len(matches)
        Library(self.library_name).create(self.folder_name)

        from pymongo import MongoClient
        client = MongoClient()
        db = client[self.library_name]

        self.assertIs(count, db.tags.count())

    def test_should_fetch_track_details(self):
        library = Library(self.library_name).create(self.folder_name)
        library_filter = library.view().by('ALBUM').filter()
        album_title = library_filter.ids[0]
        track = library_filter.using(album_title).ids[0]
        track_id = track['_id']

        tags = library.track_details(track_id)
        self.assertTrue(tags)

    def test_make_nested_view(self):
        library = Library(self.library_name).create(self.folder_name, None)
        tracks = library.view().\
            by('COMPOSER').\
            by('GENRE').\
            by('ALBUM').\
            filter().\
            using('Mendelssohn').\
            using('Chamber Music').\
            using('A').\
            ids

        self.assertIsNotNone(tracks)

    def test_should_store_document(self):
        library = Library(self.library_name).create(self.folder_name, None)
        library_filter = library.view().by('ALBUM').filter()
        album_title = library_filter.ids[0]
        track = library_filter.using(album_title).ids[0]
        track_id = track['_id']
        tags = library.track_details(track_id)
        from time import time
        now = str(time() * 1000)
        tags['ALBUM'] = now

        library.store(track_id, tags)

        from pymongo import MongoClient
        client = MongoClient()
        db = client[self.library_name]
        self.assertEquals(now, db.tags.find_one({'_id': track_id})['ALBUM'])

    def test_should_save_tags(self):
        library = Library(self.library_name).create(self.folder_name, None)
        library_filter = library.view().by('ALBUM').filter()
        album_title = library_filter.ids[0]
        track = library_filter.using(album_title).ids[0]
        track_id = track['_id']
        tags = library.track_details(track_id)
        from time import time
        now = str(time() * 1000)
        tags['ALBUM'] = now

        library.store(track_id, tags)

        path = tags['PATH']
        from tags.tagreader import TagReader
        saved_tags = TagReader().readfile(path)
        self.assertEquals(now, saved_tags['ALBUM'])
