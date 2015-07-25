__author__ = 'Massimiliano'

import os.path
from mutagen import flac


def _gettagname(tagname, tagvalue, dictionary):
    dictionary[tagname.upper()] = tagvalue;


class TagReader:
    def readfile(self, filename):
        if not os.path.isfile(filename):
            raise ValueError('Input file {0} does not exist'.format(filename))
        tags = flac.FLAC(filename).tags
        result = self.__todictionary(tags)
        return result

    def __todictionary(self, tags):
        dictionary = {}
        [(tagName, _gettagname(tagName, tagValue, dictionary)) for (tagName, tagValue) in tags]
        return dictionary
