import os,sys,thread
from socket import *
import argparse

class Proxy:

    def __init__(self, host, port):
        self.server_sock = socket(AF_INET, SOCK_STREAM)
        self.server_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server_sock.bind((host, port))
        self.server_sock.listen(300)
    
    def main(self):
        while True:
            clientsock, clientaddr = self.server_sock.accept()
            thread.start_new_thread(self.handler, (clientsock,)) 
        self.server_sock.close()


    def handler(self, client_sock):
        request = client_sock.recv(1049000)
        url = request.split(' ')[1]
        pos = url.find("://")
        clihost = url[(pos+3):]
        opos = clihost.find("/")
        trueurl = clihost[:opos]

        try:
            s = socket(AF_INET, SOCK_STREAM)  
            s.connect((trueurl, 80))
            s.send(request)

            while True:
                serverdata = s.recv(1049000)
                if not serverdata: break
                else:
                    client_sock.send(serverdata)
                    s.close()
                    client_sock.close()
            
        except error, (value, message):
            if s:
                s.close()
            if client_sock:
                client_sock.close()
            print "Runtime Error:", message
            sys.exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Web proxy with caching. Default host is localhost, default port is 1234')
    parser.add_argument('-p', '--port', help = 'port', type=int)
    parser.add_argument('-s', '--host', help = 'host')
    args = parser.parse_args()
    port = args.port
    host = 'localhost'
    if args.port: port = args.port
    if args.host: host = args.host
    p = Proxy(host, port)
    p.main()
