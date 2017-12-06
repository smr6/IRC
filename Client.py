import select, socket, sys
from Util import Room, Hall, User
import Util

READ_BUFFER = 4096
HOST = "localhost"

if len(sys.argv) >= 2:
    print("No arguments needed.", file = sys.stderr)
    sys.exit(1)
else:
    server_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_connection.connect((HOST, Util.PORT))

def prompt():
    print('>', end=' ', flush = True)

print("Connected to server\n")
msg_prefix = ''

socket_list = [sys.stdin, server_connection]

while True:
    read_sockets, write_sockets, eror_sockets = select.select(socket_list, [], [])
    for s in read_sockets:
        if s is server_connection:
            msg = s.recv(READ_BUFFER)
            if not msg:
                print("Server down!")
                sys.exit(2)
            else:
                if msg == Util.QUIT_STRING.encode():
                    sys.stdout.write('Bye\n')
                    sys.exit(2)
                else:
                    sys.stdout.write(msg.decode())
                    if 'Please tell us your name' in msg.decode():
                        msg_prefix = 'name: '
                    else:
                        msg_prefix = ''
                    prompt()

        else:
            msg = msg_prefix + sys.stdin.readline()
            server_connection.sendall(msg.encode())
