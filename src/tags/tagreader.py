__author__ = 'Massimiliano'

import os.path
import glob
from mutagen import flac


def _gettagname(tagname, tagvalue, dictionary):
    dictionary[tagname.upper()] = tagvalue;


class TagReader:
    def readfile(self, filename):
        if not os.path.isfile(filename):
            raise ValueError('Input file {0} does not exist'.format(filename))
        tags = flac.FLAC(filename).tags
        result = self.__to_dictionary(tags)
        result['PATH'] = os.path.abspath(filename)
        return result

    def readfolder(self, foldername):
        files = glob.glob(foldername + '/*.flac')
        return {file: self.readfile(file) for file in files}

    def __to_dictionary(self, tags):
        dictionary = {}
        [(tagName, _gettagname(tagName, tagValue, dictionary)) for (tagName, tagValue) in tags]
        return dictionary
