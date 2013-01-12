import os,sys,thread
from socket import *
import sys

HOST = 'localhost'
PORT = 1337

class LinkedList:
    def __init__(self, head=None, tail=None, maxsize=10490000, currentsize=0):
        self.count = 0
        self.head = head
        self.tail = tail
        self.maxsize = maxsize
        self.currentsize = currentsize
        
    def get(self, nodekey):
        currNode = self.head
        while(currNode != self.tail):
            if currNode.key == nodekey:
                return currNode
            else:
                currNode = currNode.next
        if currNode != self.tail:
            return None
        else:
            return self.tail

    def push(self, mynode):
        if self.head != None:
            temp = self.head
            self.head = mynode
            self.head.next = temp
            temp.prev = mynode

    def append(self, myobject):
        new_node = myobject

        if self.currentsize + new_node.size < self.maxsize:
            if self.head == None:
                self.head = new_node
                self.tail = new_node
            else:
                temp = self.head
                self.head = new_node
                self.head.next = temp
                temp.prev = new_node
                
            self.currentsize += new_node.size 
        else:
            self.deleteTail()
            self.append(new_node)        
        self.count += 1
        
    def deleteTail(self):
        self.currentsize -= self.tail.size
        if self.count > 1:
            temp = self.tail.prev  
            del cache[self.tail.key]
            temp = self.tail
        else:    
            self.head = None
            self.tail = None
        self.count -= 1

class Node:
    def __init__(self, prev=None, next=None, size=None, key=None, data=None):
        self.prev = prev
        self.next = next
        self.size = size
        self.key = key
        self.data = data
        
cache = {}
if len(sys.argv) < 2:
    l = LinkedList()
else:
    l = LinkedList(maxsize = sys.argv[1])

def proxy(client_sock, client_addr):

    request = client_sock.recv(1049000)
    first_line = request.split('\n')[0]
    url = first_line.split(' ')[1]

    http_pos = url.find("://")
    temp = url[(http_pos+3):]
    url_pos = temp.find("/")
    if url_pos == -1:
        url_pos = len(temp)
    URL = temp[:url_pos]
    
    if url in cache:
        print "Cache hit!"
        serverdata = cache[url].data
        print serverdata
        client_sock.send(serverdata)
        client_sock.close()
        foundnode = l.get(url)
        l.push(foundnode)
          
    else:
        print "Cache miss!"
        try:
            s = socket(AF_INET, SOCK_STREAM)  
            s.connect((URL, 80))
            s.send(request)

            while True:
                serverdata = s.recv(1049000)
                if (len(serverdata) > 0):
                    newNode = Node(key=url, data=serverdata, size=sys.getsizeof(serverdata))
                    cache[url] = newNode
                    l.append(newNode)
                    client_sock.send(serverdata)
                else:
                    break
            s.close()
            client_sock.close()
            
        except error, (value, message):
            if s:
                s.close()
            if client_sock:
                client_sock.close()
            print "Runtime Error:", message
            sys.exit(1)

def main():
    try:
        server_sock = socket(AF_INET, SOCK_STREAM)
        server_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        server_sock.bind((HOST, PORT))
        server_sock.listen(200)
    
    except error, (value, message):
        if server_sock:
            server_sock.close()
        print "Could not open socket:", message
        sys.exit(1)

    while True:
        clientsock, clientaddr = server_sock.accept()
        thread.start_new_thread(proxy, (clientsock, clientaddr))
        
    server_sock.close()

if __name__ == '__main__':
    sys.exit (main())
