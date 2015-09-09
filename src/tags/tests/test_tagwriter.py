__author__ = 'Massimiliano'
import unittest
from tags.tagwriter import TagWriter
from tags.tagreader import TagReader

class TagWriterTest(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.filename = './test-01.flac'

    def test_should_write_tags(self):
        writer = TagWriter()
        from time import time
        now = str(time() * 1000)
        tags = {
            'ALBUM': now
        }
        writer.write(tags, self.filename)
        reader = TagReader()
        document = reader.readfile(self.filename)
        self.assertEqual(document['ALBUM'], now)

    def test_should_not_override_existing_values(self):
        reader = TagReader()
        title = reader.readfile(self.filename)['TITLE']
        writer = TagWriter()
        from time import time
        now = str(time() * 1000)
        tags = {
            'ALBUM': now
        }
        writer.write(tags, self.filename)
        self.assertEqual(title, reader.readfile(self.filename)['TITLE'])
