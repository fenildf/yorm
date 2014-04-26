# before

class MyClass:

    def __init__(self, arg1, arg2, kwargs1='value1', kwarg2='value2'):
        self.arg1 = arg1
        self.arg2 = arg2
        self.kwarg2 = kwarg1
        self.kwarg2 = kwarg2

    def a_method(self, arg):
        print(arg)

class MyClass:

    def __init__(self, arg1, arg2, kwargs1='value1', kwarg2='value2'):
        self.arg1 = arg1
        self.arg2 = arg2
        self.kwarg2 = kwarg1
        self.kwarg2 = kwarg2

    def a_method(self, arg):
        print(arg)

# after

from yorm import Yobject, Yattr

class MyClassYormalized(Yobject):

    arg1 = Yattr()

    def __init__(self, arg1, arg2, kwargs1='value1', kwarg2='value2'):
        self.arg2 = arg2
        self.kwarg2 = kwarg1
        self.kwarg2 = kwarg2

    def a_method(self, arg):
        print(arg)
