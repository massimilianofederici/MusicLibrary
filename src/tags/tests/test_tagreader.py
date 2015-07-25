__author__ = 'Massimiliano'

from tags.tagreader import TagReader
import unittest
from mutagen import flac
import sys


class TagReaderTest(unittest.TestCase):
    def setUp(self):
        self.filename = './test-01.flac'
        self.expectedDocument = {}

    def test_document_should_not_be_null(self):
        reader = TagReader()
        document = reader.readfile(self.filename)
        self.assertIsNotNone(document, 'Expecting tag document not to be null')

    def test_document_should_not_be_empty(self):
        reader = TagReader()
        document = reader.readfile(self.filename)
        self.assertTrue(document, 'Expecting not empty document')

    def test_should_check_that_file_exists(self):
        reader = TagReader()
        self.assertRaises(ValueError, reader.readfile, 'invalid.flac')

    def test_should_read_file_content(self):
        reader = TagReader()
        tags = flac.FLAC(self.filename).tags

        document = reader.readfile(self.filename)

        [(tagName, self._getTagName(tagName, tagValue)) for (tagName, tagValue) in tags]
        self.assertEqual(self.expectedDocument['ALBUM'], document['ALBUM'])
        self.assertEqual(self.expectedDocument['ARTIST'], document['ARTIST'])

    def test_document_keys_should_be_uppercase(self):
        reader = TagReader()

        document = reader.readfile(self.filename)

        {value: self.assertTrue(value.isupper(), 'Expecting key to be upper but was {0}'.format(value)) for value in document}

    def _getTagName(self, tagname, tagvalue):
        self.expectedDocument[tagname.upper()] = tagvalue;
