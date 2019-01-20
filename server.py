import socket
import time
import struct
import threading
from queue import Queue

import group
import goals


# def write_modified_utf8(string):
#     utf8 = string.encode()
#     l = len(utf8)
#     result = struct.pack('!H', l)
#     format = '!' + str(l) + 's'
#     result += struct.pack(format, utf8)
#     return resul


class Server(threading.Thread):
    def __init__(self, ip, port, register_port, queue: Queue, player_queue: Queue):
        super().__init__()

        self.queue = queue
        self.player_queue = player_queue

        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind((ip, port))
        self.s.setblocking(False)

        self.register_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.register_socket.bind((ip, register_port))
        self.register_socket.setblocking(False)
        self.client_directions = []
        self.client_ips = []
        self.client_names = []

    def run(self):
        while True:
            try:
                received, addr = self.register_socket.recvfrom(256)
                print("registration pending from ", addr)

                new_name = received.decode('utf-8')
                new_id = len(self.client_directions)

                new_goals = goals.random_goals()
                encoded_goals = "\n".join(new_goals).encode()
                message = struct.pack(f'>i{len(encoded_goals)}s', new_id, encoded_goals)
                print(message)
                self.register_socket.sendto(message, addr)
                print("registered name ", new_name)

                new_player = group.Player(None, new_id, new_name)
                self.player_queue.put(new_player)

                self.client_names.append(received.decode('utf-8'))
                self.client_ips.append(addr[0])
                self.client_directions.append(None)

            except BlockingIOError:
                pass

            try:
                received, addr = self.s.recvfrom(128)
                id, direction = struct.unpack('>ii', received)
                print("direction sent by", id, self.client_names[id])
                if id >= len(self.client_directions):
                    continue
                self.client_directions[id] = direction

            except BlockingIOError:
                pass

            while not self.queue.empty():
                _ = self.queue.get()

            self.queue.put(self.client_directions)
            time.sleep(0.001)


if __name__ == '__main__':

    q = Queue()
    q2 = Queue()
    server = Server("0.0.0.0", 6666, 6665, q, q2)
    server.start()
    while True:
        info = q.get()
        print(info)
        time.sleep(1)
