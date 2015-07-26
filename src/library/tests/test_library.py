__author__ = 'Massimiliano'

import unittest
from library.library import Library


class TestLibrary(unittest.TestCase):
    def setUp(self):
        self.library_name = 'TestLibrary'
        self.folder_name = '.'
        from pymongo import MongoClient
        self.client = MongoClient()
        self.client.drop_database(self.library_name)

    def test_should_save_library_state(self):
        from glob import glob
        count = len(glob(self.folder_name + '/*.flac'))

        Library(self.library_name).create('.')

        from pymongo import MongoClient
        client = MongoClient()
        db = client[self.library_name]

        self.assertIs(count, db.tags.count())

    def test_should_list_tracks_by_album(self):
        library = Library(self.library_name).create(self.folder_name)
        albums = library.view_albums()

        for album in albums:
            tracks = library.view_tracks_by_album(album)
            self.assertTrue(tracks)
            for track in tracks:
                self.assertIsNotNone(track['TITLE'])
                self.assertIsNotNone(track['TRACKNUMBER'])
                self.assertIsNotNone(track['_id'])

    def test_should_fetch_track_details(self):
        library = Library(self.library_name).create(self.folder_name)
        album_title = library.view_albums()[0]
        track = library.view_tracks_by_album(album_title)[0]
        track_id = track['_id']

        tags = library.track_details(track_id)
        self.assertTrue(tags)

    def test_make_nested_view(self):
        library = Library(self.library_name).create(self.folder_name)
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

    def test_should_sort_tracks_by_track_number(self):
        library = Library(self.library_name).create(self.folder_name)
        tracks = library.view_tracks_by_album('A')
        self.assertIs('1', tracks[0]['TRACKNUMBER'])
        self.assertIs('2', tracks[1]['TRACKNUMBER'])
