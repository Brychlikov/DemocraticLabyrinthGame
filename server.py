import json
import socket
import time
import struct
import threading
from queue import Queue

from loguru import logger

import group
import goals

logger.debug("Server imported")

# def write_modified_utf8(string):
#     utf8 = string.encode()
#     l = len(utf8)
#     result = struct.pack('!H', l)
#     format = '!' + str(l) + 's'
#     result += struct.pack(format, utf8)
#     return resul


class Server(threading.Thread):
    def __init__(self, ip, port, register_port, queue: Queue, player_queue: Queue, goal_queue: Queue, info_queue: Queue):
        super().__init__()

        self.queue = queue
        self.player_queue = player_queue
        self.goal_queue = goal_queue
        self.info_queue = info_queue

        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind((ip, port))
        self.s.setblocking(False)

        self.halt = False

        self.register_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.register_socket.bind((ip, register_port))
        self.register_socket.setblocking(False)
        self.client_directions = []
        self.client_adresses = []
        self.client_names = []

    @logger.catch
    def run(self):
        logger.debug("Server thread started")
        while True:
            if self.halt:
                logger.debug("Server got termination signal")
                break
            try:
                received, addr = self.register_socket.recvfrom(256)
                logger.trace(f"registration pending from {addr}")

                new_name = received.decode('utf-8')
                new_id = len(self.client_directions)
                new_player = group.Player(None, new_id, new_name)
                self.player_queue.put(new_player)
                logger.info(f"Registered new player with name {new_name} and id {new_id}")

                new_goals = self.goal_queue.get()
                logger.trace("New player data exchange finished")
                encoded_goals = "\n".join(new_goals).encode()
                message = struct.pack(f'>i{len(encoded_goals)}s', new_id, encoded_goals)
                self.register_socket.sendto(message, addr)
                logger.trace("Goals sent to client")

                self.client_names.append(received.decode('utf-8'))
                self.client_adresses.append(addr)
                self.client_directions.append(None)

            except BlockingIOError:
                pass

            try:
                received, addr = self.s.recvfrom(128)
                id, direction = struct.unpack('>ii', received)
                logger.trace(f"Direction received. id: {id} direction: {direction}")
                if id >= len(self.client_directions):
                    logger.warning("Direction request from unknown id")
                    continue
                self.client_directions[id] = direction

            except BlockingIOError:
                pass

            while not self.queue.empty():
                _ = self.queue.get()
            self.queue.put(self.client_directions)

            if not self.info_queue.empty():
                data = self.info_queue.get()
                for player in data:
                    player_address = self.client_adresses[player["id"]]
                    json.dump(player, open("example_dump.json", "w"))
                    to_send = json.dumps(player).encode()
                    self.s.sendto(to_send, (player_address[0], 5554))
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
