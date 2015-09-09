__author__ = 'Massimiliano'
from mutagen.flac import FLAC
from mutagen.flac import Picture


class TagWriter:

    def write(self, tags, file_name):
        flac_file = FLAC(file_name)
        for key in tags:
            if key != '_id':
                flac_file.tags[key] = tags[key]
        flac_file.save(file_name)

    def replace_picture(self, picture_data, file_name):
        flac_file = FLAC(file_name)
        flac_file.clear_pictures()
        picture = Picture()
        picture.data = picture_data
        flac_file.add_picture(picture)
        flac_file.save(filename=file_name)


