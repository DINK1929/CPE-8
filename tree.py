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

root = TreeNode(1)
root.left = TreeNode(2)
root.right = TreeNode(3)
root.left.right = TreeNode(5)
root.left.left = TreeNode(4)
root.right.left = TreeNode(6)
root.right.right = TreeNode(7)

print("In-Order Traversal")
InOrderTraversal(root)
print("\nPre-order Traversal")
PreOrderTraversal(root)
print("\nPost-order Traversal")
PostOrderTraversal(root)
