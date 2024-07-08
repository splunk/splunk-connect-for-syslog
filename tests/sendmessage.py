# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

import socket
from time import sleep
import os


def sendsingle(message, host, port, use_udp=False):

    socket_type = socket.SOCK_DGRAM if use_udp else socket.SOCK_STREAM
    sock = socket.socket(socket.AF_INET, socket_type)
    server_address = (host, port)

    if use_udp:
        sock.sendto(str.encode(message), server_address)
    else:
        tried = 0
        while True:
            try:
                sock.connect(server_address)
                break
            except socket:
                tried += 1
                if tried > 90:
                    raise
                sleep(1)
        sock.sendall(str.encode(message))
    sock.close()
