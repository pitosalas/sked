class Clock:
    """
    A class representing a clock that can be incremented and observed by registered objects.
    """

    def __init__(self):
        self.watchers = []
        self.time = 0

    def log(self, message):
        if False: print(message)

    def increment(self):
        for obj in self.watchers:
            obj.update(self.time)
        self.log(f"\n***Incrementing: {self.time} watchers: {len(self.watchers)}***\n" )
        self.time += 1

    def get_time(self):
        return self.time

    def register_object(self, obj):
        self.watchers.append(obj)

    def unregister_object(self, obj):
        self.watchers.remove(obj)

