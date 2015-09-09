__author__ = 'Massimiliano'

from abc import abstractmethod
import os.path
from mutagen import flac
import fnmatch


def _get_tag_name(tagname, tagvalue, dictionary):
    dictionary[tagname.upper()] = tagvalue


class TagReaderListener:

    @abstractmethod
    def counting_files(self):
        pass

    @abstractmethod
    def read_start(self, count):
        pass

    @abstractmethod
    def file_read(self, file):
        pass

    @abstractmethod
    def file_error(self, file):
        pass

    @abstractmethod
    def read_complete(self, elapsed_time):
        pass


class NullListener(TagReaderListener):

    def counting_files(self):
        pass

    def file_error(self, file):
        pass

    def read_start(self, count):
        pass

    def read_complete(self, elapsed_time):
        pass

    def file_read(self, file):
        pass


class TagReader:

    def readfile(self, filename, listener=NullListener()):
        if not os.path.isfile(filename):
            raise ValueError('Input file {0} does not exist'.format(filename))
        tags = flac.FLAC(filename).tags
        result = self.__to_dictionary(tags)
        result['PATH'] = os.path.abspath(filename)
        if listener:
            listener.file_read(filename)
        return result

    def readfolder(self, foldername, listener=NullListener()):
        from time import time
        start = time()
        matches = []
        listener.counting_files()
        for root, dirnames, filenames in os.walk(foldername):
            for filename in fnmatch.filter(filenames, "*.flac"):
                matches.append(os.path.join(root, filename))
        listener.read_start(len(matches))
        tags = {file: self.readfile(file, listener) for file in matches}
        listener.read_complete(time() - start)
        return tags

    @staticmethod
    def read_pictures(file_name):
        return flac.FLAC(file_name).pictures

    def __to_dictionary(self, tags):
        dictionary = {}
        [(tagName, _get_tag_name(tagName, tagValue, dictionary)) for (tagName, tagValue) in tags]
        return dictionary
