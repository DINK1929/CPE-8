class TreeNode:
    def __init__(self,value):
        self.value = value
        self.left = None
        self.right = None

#In-Order
def InOrderTraversal(root):
    if root:
        InOrderTraversal(root.left)
        print(root.value, end=" ")
        InOrderTraversal(root.right)

def SwapInOrderTraversal(root):
    if root:
        SwapInOrderTraversal(root.right)
        print(root.value, end=" ")
        SwapInOrderTraversal(root.left)

#Pre-Order
def PreOrderTraversal(root):
    if root:
        print(root.value, end=" ")
        PreOrderTraversal(root.left)
        PreOrderTraversal(root.right)

#Post Order
def PostOrderTraversal(root):
    if root:
        PostOrderTraversal(root.left)
        PostOrderTraversal(root.right)
        print(root.value, end=" ")

def swap_roots(root):
    if root:
        root.left, root.right = root.right, root.left
        swap_roots(root.left)
        swap_roots(root.right)

root = TreeNode(1)
root.left = TreeNode(2)
root.right = TreeNode(3)
root.left.right = TreeNode(5)
root.left.left = TreeNode(4)
root.right.left = TreeNode(6)
root.right.right = TreeNode(7)

print("\nPre-order Traversal")
PreOrderTraversal(root)
print("\nIn-Order Traversal")
InOrderTraversal(root)
print("\nPost-order Traversal")
PostOrderTraversal(root)

print("\n\nSwapping Subtrees")
swap_roots(root)

print("\nIn-Order Traversal after swap:")
InOrderTraversal(root)
print("\nPre-order Traversal after swap:")
PreOrderTraversal(root)
print("\nPost-order Traversal after swap:")
PostOrderTraversal(root)


