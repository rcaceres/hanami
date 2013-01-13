__doc__ = """Web Proxy.

This module behaves as an HTTP proxy. It implements
GET methods.

2013/13/1 - Created by Eddie Figueroa
            * Added very simple GET request
            * Restructured to use Select module instead
              of multithreading for efficiency
            * Added support for optional flags
"""
__version__ = "2.0.0"

import select
import sys
import Queue
import argparse
import urllib2
from socket import *

BUFFER_SIZE = 4096

class Proxy:

    def __init__(self):
        
        # Create a TCP/IP socket
        self.server = socket(AF_INET, SOCK_STREAM)
        self.server.setblocking(0)
        self.server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

        # Parse command-line arguments to check for host, port
        arg = self.getargs()

        # Bind socket to host, port
        self.server.bind((arg[0], arg[1]))

        # Listen for incoming connections
        self.server.listen(200)

        # Sockets from which are ready to be read
        self.inputs = [ server ]

        # Sockets from which are ready to be written to
        self.outputs = []

        # Queues of content received from Internet to be sent to Browser
        self.content_queues = {}

    def getargs(self):
        parser = argparse.ArgumentParser(description='Caching Web Proxy. Default host is localhost, default port is 8080')
        parser.add_argument('-s', '--host', help = 'host')
        parser.add_argument('-p', '--port', help = 'port', type=int)
        args = parser.parse_args()

        # If not specified, default host, port are given
        host = 'localhost'
        port = 8080
        if args.host: host = args.host
        if args.port: port = args.port

        # Return tuple
        return host, port

    def on_accept(self, readsock):
        # A readable socket is ready to accept a connection and be read from
        clientsock, clientaddr = readsock.accept()
        clientsock.setblocking (0)
        self.inputs.append(clientsock)

        # Create a new entry in the hashtable for this client for data we want to send
        self.content_queues[clientsock] = Queue.Queue()

    def on_recv(self, readsock, content):
        # content variable is an http header, a huge blob of words
        # Snag URL from header, it's all we need
        url = request.split(' ')[1]

        # Instead of using sockets to request data from remote server, we use urllib2 for simplicity and convenience
        response = urllib2.urlopen(url).read()
        self.content_queues[readsock].put(response)

        # Add socket to output channel so we can send it from our proxy to the browser
        if readsock not in self.outputs:
            self.outputs.append(readsock)
    
    def on_close(self, readsock):
        # Empty result is a closed connection
        if readsock in self.outputs:
            self.outputs.remove(readsock)
        self.inputs.remove(readsock)
        readsock.close()
        del self.content_queues[readsock]

    def on_write(self, writesock):
        try:
            # Send content from remote server to browser client
            msg = self.content_queues[writesock].get_nowait()
            writesock.send(msg)

        except Queue.Empty:
            # Stop checking for writeability
            self.outputs.remove(writesock)

    def main_loop(self):
        while self.inputs:            
            # Wait for at least one socket to be ready
            readable, writeable, exceptional = select.select(self.inputs, self.outputs, self.inputs)
            
            #Inputs
            for readsock in readable:
                # If readable socket is actually the proxy's socket
                if readsock is self.server:
                    self.on_accept(readsock)

                # If readable socket is a client socket
                else:
                    data = readsock.recv(BUFFER_SIZE)
                    if data:
                        self.on_recv(readsock, data)
                    else:
                        self.on_close()

            # Outputs
            for writesock in writeable:
                # If writeable socket is ready to be written to
                self.on_write(writesock)

if __name__ == '__main__':
    p = Proxy()
    sys.exit(p.main_loop())
