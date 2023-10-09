class X:
    def __init__(self):
        self.name = "base"


class Y(X):
    def __init__(self):
        self.name = "sub"
        super().__init__()


x = X()
print(x.name)

y = Y()
print(y.name)
