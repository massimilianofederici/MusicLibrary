import socketserver
import copy
from json import loads
from json import dumps
from library.library import Library

__author__ = 'Massimiliano'


class LibraryServer(socketserver.TCPServer):
    library = None


class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024).strip()
        data = loads(data.decode())
        print("{} wrote:".format(self.client_address[0]))
        command = next(iter(data.keys()))
        argument = data[command]
        result = getattr(self, command)(argument)
        self.request.sendall(dumps(result).encode())

    def choose_library(self, library_name):
        self.server.library = Library(library_name).restore()
        command = {'query': {},
                   'view': 'COMPOSER'}
        return self.view_library(command)

    def view_library(self, query_param):
        query = query_param['query']
        view = query_param['view']
        return [{'label': item, 'type': view, 'item': self.__make_node_id(query, view, item)}
                for item in self.server.library.aggregate(query, view)]

    @staticmethod
    def __make_node_id(parent_node, node_type, node_value):
        node_id = {}
        if parent_node:
            node_id = copy.copy(parent_node)
        node_id[node_type] = node_value
        return node_id


if __name__ == "__main__":
    HOST, PORT = "192.168.0.4", 10000
    print("Listening on port {}".format(PORT))
    server = LibraryServer((HOST, PORT), MyTCPHandler)
    server.serve_forever()
