LOGGING = True
class Clock:
    """
    A class representing a clock that can be incremented and observed by registered objects.
    """

    def __init__(self):
        self.watchers = []
        self.time = 0

    def log(self, message):
        if LOGGING: print(message)

    def increment(self):
       self.log(f"\n***Incrementing: from {self.time} to {self.time+1} watchers: {len(self.watchers)}***\n" )
       self.time += 1
       for obj in self.watchers:
            obj.update(self.time)

    def get_time(self):
        return self.time

    def register_object(self, obj):
        self.watchers.append(obj)

    def unregister_object(self, obj):
        self.watchers.remove(obj)

