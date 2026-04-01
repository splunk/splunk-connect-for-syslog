# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

import socket
from time import sleep


def sendsingle(message, host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (host, port)

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
