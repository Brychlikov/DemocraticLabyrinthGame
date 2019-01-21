import socket
import time
import struct

IP = "0.0.0.0"
REG_PORT = 6665
INFO_PORT = 6666


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("0.0.0.0", 5555))
while True:
    ans = input("Option: ")
    if ans == "r":
        s.sendto("Roman".encode('utf-8'), (IP, REG_PORT))
        print("Registration request sent")
        received, adr = s.recvfrom(512)
        got_id = struct.unpack('>i', received[:4])
        print("got signed id:", got_id)
        print("got goals: ", received[4:].decode())

    if len(ans) == 3 and ans[0] == 's':
        print("attempting sending")
        to_send = struct.pack('>ii', int(ans[1]), int(ans[2]))
        s.sendto(to_send, (IP, INFO_PORT))



