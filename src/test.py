class A:
    def __init__(self,a = 0):
        self.a = a

x = A()
print(hasattr(x, 'b'))