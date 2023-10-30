class Queue:
    def __init__(self, name: str):
        self.name = name
        self._list = []

    def add_at_end(self, pcb):
        pcb.status = self.name
        self._list += [pcb]

    def remove_from_front(self):
        pcb = self._list[0]
        self._list = self._list[1:]
        return pcb

    def remove(self, pcb):
        self._list.remove(pcb)
        return pcb

    def length(self):
        return len(self._list)

    def empty(self):
        return len(self._list) == 0

    @property
    def head(self):
        if len(self._list) > 0:
            return self._list[0]
        else:
            return None

    def pids_string(self):
        return f"[{', '.join([pcb.pid for pcb in self._list])}]"
    
    def __repr__(self):
        return f"Queue {self.name}"
