import socket, pdb

MAX_CLIENTS = 30
PORT = 8000
QUIT_STRING = '/$quit$'


def create_socket(address):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setblocking(0)
    s.bind(address)
    s.listen(MAX_CLIENTS)
    print("Now listening at ", address)
    return s

class Hall:
    def __init__(self):
        self.rooms = {}
        self.room_user_map = {}

    def welcome_new(self, new_user):
        new_user.socket.sendall(b'Welcome to the chat!\nPlease tell us your name:\n')
        
    def list_rooms(self, user):
        
        if len(self.rooms) == 0:
            msg = 'Oops, no active rooms currently. Create your own!\n' \
                + 'Use [/join room_name] to create a room.\n'
            user.socket.sendall(msg.encode())
        else:
            msg = 'Listing current rooms...\n'
            for room in self.rooms:
                msg += room + ": " + str(len(self.rooms[room].users)) + " user(s)\n"
            user.socket.sendall(msg.encode())

    def handle_msg(self, user, msg):
        
        instructions = b'Instructions:\n'\
            + b'[/list] to list all rooms\n'\
            + b'[/join room_name] to join/create a room\n' \
            + b'[/leave room_name] to leave a room\n' \
            + b'[/manual] to show instructions\n' \
            + b'[/quit] to quit\n' \
            + b'Otherwise start typing and enjoy!' \
            + b'\n'

        print(user.name + " says: " + msg)
        
        if "name:" in msg:
            name = msg.split()[1]
            user.name = name
            print("New connection from: ", user.name)
            user.socket.sendall(instructions)

        elif "/join" in msg:
            same_room = False
            if len(msg.split()) >= 2:
                room_name = msg.split()[1]
                if user.name in self.room_user_map:
                    if self.room_user_map[user.name] == room_name:
                        user.socket.sendall(b'You are already in room ' + room_name.encode())
                        same_room = True
                if not same_room:
                    if not room_name in self.rooms:
                        new_room = Room(room_name)
                        self.rooms[room_name] = new_room
                    self.rooms[room_name].users.append(user)
                    self.rooms[room_name].welcome_new(user)
                    self.room_user_map[user.name] = room_name
            else:
                user.socket.sendall(instructions)

        elif "/leave" in msg:
            if len(msg.split()) >= 2:
                room_name = msg.split()[1]
                if user.name in self.room_user_map:
                    if self.room_user_map[user.name] == room_name:                   
                        self.rooms[self.room_user_map[user.name]].remove_user(user)
                    else:
                        user.socket.sendall(b'You are not in room ' + room_name.encode())
                    
                    
        #elif "/who" in msg:
        #    if len(msg.split()) >= 2:
        #        room_name = msg.split()[1]
        #        print('Users in ' + room_name + ': '
        #        for user.name in self.room_user_map:
        #            print(user.name + '\n')

        elif "/list" in msg:
            self.list_rooms(user)

        elif "/manual" in msg:
            user.socket.sendall(instructions)

        elif "/quit" in msg:
            user.socket.sendall(QUIT_STRING.encode())
            self.remove_user(user)

        else:
            if user.name in self.room_user_map:
                self.rooms[self.room_user_map[user.name]].broadcast(user, msg.encode())
            else:
                msg = 'You are currently not in any room! \n' \
                    + 'Use [/list] to see available rooms! \n' \
                    + 'Use [/join room_name] to join a room! \n'
                user.socket.sendall(msg.encode())

    def remove_user(self, user):
        if user.name in self.room_user_map:
            self.rooms[self.room_user_map[user.name]].remove_user(user)
            del self.room_user_map[user.name]
        print(user.name + " has left the room\n")


class Room:
    def __init__(self, name):
        self.users = []
        self.name = name

    def welcome_new(self, from_user):
        msg = self.name + " welcomes: " + from_user.name + '\n'
        for user in self.users:
            user.socket.sendall(msg.encode())

    def broadcast(self, from_user, msg):
        msg = from_user.name.encode() + b": " + msg
        for user in self.users:
            user.socket.sendall(msg)

    def remove_user(self, user):
        self.users.remove(user)
        leave_msg = user.name.encode() + b" has left the room\n"
        self.broadcast(user, leave_msg)

class User:
    def __init__(self, socket, name = "new"):
        socket.setblocking(0)
        self.socket = socket
        self.name = name

    def fileno(self):
        return self.socket.fileno()
