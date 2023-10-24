import functools


class Test:

    def __init__(self):
        self.indent = 0

    def logger(self, func):
        def wrapper(self, *args, **kwargs):
            print('|' * self.indent + 'Entering', func.__name__)
            self.indent += 1

            value = func(self, *args, **kwargs)

            self.indent -= 1
            print('|' * self.indent + 'Exiting', func.__name__)
            return value

        return wrapper

    @logger
    def foo(self):
        print('In foo')
        self.bar()

    @logger
    def bar(self):
        print('In bar')


test = Test()
test.foo()
