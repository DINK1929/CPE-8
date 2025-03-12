class Node:
    def __init__(self,data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None

    def insert(self, data):
        new_node = Node(data)

        if not self.head:
            self.head = new_node
            return

        last = self.head
        while last.next:
            last.next = new_node

    def print_recursion(self,node):
        if node is Node:
            return
        print(node.data)
        self.print_recursion(node.next)

    def start_recursion_traversal(self):
        self.print_recursion(self.head)

if __name__ == "__main__":
    linkedlist = LinkedList()

    linkedlist.insert(5)
    linkedlist.insert(10)
    linkedlist.insert(15)
    linkedlist.insert(20)
    linkedlist.insert(25)

    print("Linked List")
    linkedlist.start_recursion_traversal()