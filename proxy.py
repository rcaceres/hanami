__doc__ = """Web Proxy.

This module behaves as an HTTP proxy. It implements
GET methods. It has a least-recently used cache.

2013/13/1 - Created by Eddie Figueroa
            * Added LRU-cache
            * Added debugging variables
            * Added more documentation
"""
__version__ = "3.0.0"

import select
import sys
import Queue
import argparse
import urllib2
from socket import *

BUFFER_SIZE = 4096
LLIST_SIZE = 1049000
debug = True

class Proxy:

    def __init__(self):

        # Create hashtable and LinkedList object for caching
        self.cache = {}
        self.llist = LinkedList()
        
        # Counters for usage reports
        self.hitcount = 0
        self.misscount = 0
        
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
        self.inputs = [ self.server ]

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
        url = content.split(' ')[1]
        
        print "Requesting: " + url + "\n"

        # If data is in cache, do not rerequest
        if url in self.cache:
            print "Cache hit!"
            self.hitcount += 1
            cached_content = cache[url].data
            self.content_queues[readsock].put(cached_content)
            
            # Find the linked list node this url belongs to, and push it up to the front
            shift_node = self.llist.get(url)
            self.llist.push(shift_node)
        
        # If data is not in cache, request it
        else:
            print "Cache miss..."
            
            # Instead of using sockets to request data from remote server, we use urllib2 for simplicity and convenience
            response = urllib2.urlopen(url).read()
            self.content_queues[readsock].put(response)
            
            # Create and append a new node in the cache and linked list
            new_node = Node(key=url, data=response, size=sys.getsizeof(response))
            self.cache[url] = new_node
            self.llist.append(new_node)

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
            msg = self.content_queues[writesock].get()
            print "Accessing site."
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
                        self.on_close(readsock)

            # Outputs
            for writesock in writeable:
                # If writeable socket is ready to be written to
                self.on_write(writesock)

class Node:
    def __init__(self, prev=None, nex=None, size=None, key=None, data=None):
        self.prev = prev
        self.next = nex
        self.size = size
        self.key = key
        self.data = data

class LinkedList:
    def __init__(self, head=None, tail=None, maxsize=LLIST_SIZE, currentsize=0):
        self.count = 0
        self.head = head
        self.tail = tail
        self.maxsize = maxsize
        self.currentsize = currentsize

    def append(self, node):
        new_node = node

        # Checks if cache has room
        if self.currentsize + new_node.size < self.maxsize:

            # Checks if linkedlist is empty
            if not self.head:
                self.head = new_node
                self.tail = new_node
            else:
                temp = self.head
                self.head = new_node
                self.head.next = temp
                temp.prev = new_node

            # Increments size counter by new node's size
            self.currentsize += new_node.size
        
        else:
            # If there is no room, delete least recently used node (the tail), reattempt append
            self.deleteTail()
            self.append(new_node)

        # Decrement number of nodes
        self.count += 1

    def deleteTail(self):
        # Subtracts tail's size from overall size
        self.currentsize -= self.tail.size

        # Checks if it is the only element in the list
        if self.count > 1:
            temp = self.tail.prev
            del cache[self.tail.key]
            temp = self.tail
        else:
            self.head = None
            self.tail = None
            
        # Decrement number of nodes
        self.count -= 1

    # Shifts node to the head since it is the new most recently used
    def push(self, node):
        # Checks if node is head or not; if not, then push is inconsequential
        if node != self.head:
            temp = self.head
            self.head = node
            self.head.next = temp
            temp.prev = node
    
    # Finds a node given an URL, slow and needs reworking
    def get(self, nodekey):
        curr = self.head
        
        # Loops through every node in the linkedlist to find a match
        while True:
            if curr.key == nodekey:
                return curr
            else:
                curr = curr.next
            # Checks if loop has reached end of list and hasn't found a match
            if not curr:
                break

if __name__ == '__main__':
    p = Proxy()
    sys.exit(p.main_loop())
