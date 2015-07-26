__author__ = 'Massimiliano'

from library.library import Library

library_name = input("Please enter the library name\n")
library_path = input("Please enter the library path\n")
library = Library(library_name).create(library_path)
view1 = input('View library by\n')
filters = library.view().by(view1).filter()
value = input('Filter by\n')
tracks = filters.using(value).ids
for track in tracks:
    print(track.encode('UTF-8'))
