import socket


TCP_IP = 'localhost'
TCP_PORT = 9999
BUFFER_SIZE = 1024
MESSAGE = '<?xml version="1.0" encoding="UTF-8"?><PlaylistAdd uri="/music_readonly/Beethoven, Ludwig van/Chamber Music/Quartet for Strings No. 1 in F major, Op. 18-1/Tokyo String Quartet, 2012/"></PlaylistAdd>\n'

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
s.send(MESSAGE.encode())
data = s.recv(BUFFER_SIZE)
s.close()

print("received data:", data)
