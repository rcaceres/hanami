**hanami** is a tiny HTTP web proxy designed to work with your browser. It uses a recently-used caching algorithm to increase overall performance, it monitors usage statistics such as cache hits and misses, and it's designed to blacklist specific URLs. Originally multithreaded, this app was built with efficiency and speed in mind, and instead uses Selectors to monitor sockets. Give it a try.

## Installation
Currently there are no dependencies needed outside of standard Python 2.7.x.

## Running
You should run it like this:
```
python hanami.py -p [port] -s [host]
```
If you don't supply a port and host, by default it goes to 8080 and localhost. 

## Blacklisting
If you need to blacklist websites, `blacklist.py` is made up of a python list of all the sites you want the proxy to ignore. It works like this:
```
blacklist = [ 
	'http://www.example.com', 
	'http://example2.com'
]
```
Make sure to keep the websites in quotes, and delimit them with a comma.
