import socket
from json import dumps

TCP_IP = '192.168.0.4'
TCP_PORT = 10000
BUFFER_SIZE = 1024
CHOOSE_LIBRARY = {
    'choose_library': 'music1'
}

VIEW_LIBRARY = {
    'view_library': {
        'query': {},
        'view': 'COMPOSER'
    }
}

SELECT_COMPOSER = {
    'view_library': {
        'query': {
            'COMPOSER': 'Bacewicz, Grazyna'
        },
        'view': 'GENRE'
    }
}

SELECT_GENRE = {
    'view_library': {
        'query': {
            'COMPOSER': 'Bacewicz, Grazyna',
            'GENRE': 'Chamber Music'
        },
        'view': 'ALBUM'
    }
}

SELECT_ALBUM = {
    'view_library': {
        'query': {
            'COMPOSER': 'Bacewicz, Grazyna',
            'GENRE': 'Chamber Music',
            'ALBUM': 'Concertino for Violin and Piano'
        },
        'view': 'ARTIST'
    }
}

VIEW_TRACKS = {
    'view_library': {
        'query': {
            'COMPOSER': 'Bacewicz, Grazyna',
            'GENRE': 'Chamber Music',
            'ALBUM': 'Concertino for Violin and Piano',
            'ARTIST': 'Piotr Plawner, Ewa Kupiec'
        },
        'view': 'TITLE'
    }
}


def send_and_receive(message):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.send(dumps(message).encode())
    data = s.recv(BUFFER_SIZE)
    print("received data:", data)
    s.close()

send_and_receive(CHOOSE_LIBRARY)
send_and_receive(VIEW_LIBRARY)
send_and_receive(SELECT_COMPOSER)
send_and_receive(SELECT_GENRE)
send_and_receive(SELECT_ALBUM)
send_and_receive(VIEW_TRACKS)




