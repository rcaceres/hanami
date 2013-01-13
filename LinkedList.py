LLIST_SIZE = 1049000

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
