LOGGING = True


class SJF:
    def __init__(self, filename):
        self.filename = filename
        self.tick = 0
        self.local_timeline = []
        self.timeline = []
        self.running = None

    def log(self, message):
        if LOGGING:
            print(message)

# The file is a csv with 6 columns, corresponding to:
# wait, burst1, io1, burst2, io2, burst3
# The local is a list of lists, indexed by process number, and within that indexed by tick

    def generate_local_timelime(self):
        with open(self.filename, 'r') as f:
            for line in f:
                process_lt = self.process_lt(line)
                self.local_timeline.append(process_lt)

    def process_lt(self, line):
        process_lt = []
        line_split = line.split(',')
        process_lt.append(int(line_split[0])*'-')
        process_lt.append(int(line_split[0])*'c')
        process_lt.append(int(line_split[0])*'i')
        process_lt.append(int(line_split[0])*'c')
        process_lt.append(int(line_split[0])*'i')
        process_lt.append(int(line_split[0])*'c')
        return process_lt

    # timeline is a list with an entry for each process
    # each entry has a list with an entry for each elapsed tick
    # each of those entries indicates the status of process at that tick
    # those entries are a list of two items, the first is the process status and the second is
    # the local tick offset for that process. This method creates the entry for tick 0
    def initialize_time_line(self):
        self.log("*** begin of first time init***")
        first_entry = []
        self.log(f"Local timeline:{self.local_timeline}")
        for index, process in enumerate(self.local_timeline):
            first_entry.append([process[0], 0])
            self.log(first_entry)
        self.timeline.append(first_entry)
        self.log("*** end of first time init***")

    def propose_next_tick(self):
        self.tick += 1
        tick = self.tick  # just for convenience
        # first calculate it without regard to the fact that only one process can run at a time
        new_entry = []
        for index, local_state in enumerate(self.local_timeline):
            self.log(f"Propose next process: {index} {local_state}")
            if local_state[tick] == 'c':
                new_entry.append(['p', 0])
            elif local_state[tick] == 'i':
                new_entry.append(['i', 0])
            else:
                new_entry.append(['-', 0])
        self.log(f"Proposed next tick:{new_entry}\n")
        self.timeline.append(new_entry)

    def determine_run_text_tick(self):
        if self.running is not None and self.timeline[self.running][self.tick][0] == 'c':
            self.log(f'process {self.running} continues running\n')
            self.update_local_tick_offsets(self.running)
        else:
            try_running = None
            estimated_size = -1
            for index, process in enumerate(self.timeline):
                self.log(f"{index} {process}")
                if process[self.tick][0] == 'p':
                    if try_running is None:
                        try_running = index
                    elif self.job_size(index) < estimated_size:
                        try_running = index
                        estimated_size = self.job_size(index)
            if try_running is not None:
                print(f'process {try_running} begins running\n')
                self.running = try_running
                self.timeline[try_running][self.tick][0] = 'c'
            self.update_local_tick_offsets(try_running)

    def job_size(self, index):
        return 1

    # for all processes other than skip_process, we take the local tick offset from the previous tick
    # and add one to it. For the skip_process, we just copy the local tuck offset.
    def update_local_tick_offsets(self, skip_process):
        print(f"Skip Process {skip_process}")
        for index, process in enumerate(self.local_timeline):
            print(
                f"Process:{index} state:{process[self.tick]}")
            if process[self.tick][0] == 'r' and index != skip_process:
                self.local_timeline[index][self.tick][1] = self.local_timeline[index][self.tick-1][1] + 1
            elif process[self.tick][0] == 'r' and index == skip_process:
                self.local_timeline[index][self.tick][1] = self.local_timeline[index][self.tick-1][1]
            else:
                print(":error in update_local tick offsets")

    def pretty_print_timeline(self):
        for index, entry in enumerate(self.timeline):
            print(f'tick:{index}: {entry}\n')


if __name__ == '__main__':
    sjf = SJF('data0.csv')
    sjf.generate_local_timelime()
    sjf.initialize_time_line()
    sjf.pretty_print_timeline()
    # sjf.propose_next_tick()
    # sjf.determine_run_text_tick()
    # sjf.pretty_print_timeline()
    # sjf.propose_next_tick()
    # sjf.determine_run_text_tick()
    # sjf.pretty_print_timeline()
