from itertools import chain

PROCESS_IT = 0
FIRST_TIME = 1
NEXT_TICK = 2
LOCAL_TICK = 3
JOBSIZE = 4
LOGGING = [True, False, True, False, False]


class SJF:
    def __init__(self, filename):
        self.filename = filename
        self.tick = 0
        self.local_timeline = []
        self.timeline = []
        self.running = None

    def log(self, number, message):
        if LOGGING[number]:
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
        process_lt.append(int(line_split[0])*['-'])
        process_lt.append(int(line_split[1])*['c'])
        process_lt.append(int(line_split[2])*['i'])
        process_lt.append(int(line_split[3])*['c'])
        process_lt.append(int(line_split[4])*['i'])
        process_lt.append(int(line_split[5])*['c'])
        process_lt = self.flatten_chain(process_lt)
        self.log(PROCESS_IT, process_lt)
        return process_lt

    # timeline is a list with an entry for each process
    # each entry has a list with an entry for each elapsed tick
    # each of those entries indicates the status of process at that tick
    # those entries are a list of two items, the first is the process status and the second is
    # the local tick offset for that process. This method creates the entry for tick 0

    def initialize_time_line(self):
        self.log(FIRST_TIME, "*** begin of first time init***")
        first_entry = []
        self.log(FIRST_TIME, f"Local timeline:{self.local_timeline}")
        for index, process in enumerate(self.local_timeline):
            first_entry.append([process[0], 0])
            self.log(FIRST_TIME, first_entry)
        self.timeline.append(first_entry)
        self.log(FIRST_TIME, "*** end of first time init***")

    def propose_next_tick(self):
        self.tick += 1
        tick = self.tick  # just for convenience
        # first calculate it without regard to the fact that only one process can run at a time
        new_entry = []
        for index, local_state in enumerate(self.local_timeline):
            self.log(NEXT_TICK, f"Propose next process: {index} {local_state}")
            if self.get_local_state(index, tick) == 'c':
                new_entry.append(['r', 0])
            elif self.get_local_state(index, tick) == 'i':
                new_entry.append(['i', 0])
            else:
                new_entry.append(['x', 0])
        self.log(NEXT_TICK, f"Proposed next tick:{new_entry}\n")
        self.timeline.append(new_entry)

    def get_local_state(self, process, tick):
        self.log(NEXT_TICK, f"Get local state for process {process} at tick {tick}")
        if len(self.local_timeline[process]) <= tick-self.timeline[tick-1][process][1]:
            return 'x'
        else:
            return self.local_timeline[process][tick-self.timeline[tick-1][process][1]]

    def determine_run_text_tick(self):
        if self.running is not None and self.timeline[self.tick][self.running][0] == 'c':
            self.log(NEXT_TICK, f'process {self.running} continues running\n')
            self.update_local_tick_offsets(self.running)
        else:
            try_running = None
            estimated_size = -1
            current_tick = self.timeline[self.tick]
            self.log(NEXT_TICK, current_tick)

            for index, process in enumerate(current_tick):
                self.log(NEXT_TICK, f"Process:{index} state: {process}")
                if process[0] == 'r':
                    if try_running is None:
                        try_running = index
                    elif self.job_size(current_tick, index) < estimated_size:
                        try_running = index
                        estimated_size = self.job_size(current_tick, index)
            if try_running is not None:
                self.log(NEXT_TICK, f'process {try_running} begins running\n')
                self.running = try_running
                self.timeline[self.tick][try_running][0] = 'c'
                self.update_local_tick_offsets(try_running)

    def job_size(self, current_tick, target_process):
        burst_size = 0
        in_burst = False
        burst_sizes = []
        for tick_row in self.timeline:
            if tick_row[target_process][0] == 'c' and not in_burst:
            # entered burst
                burst_size += 1
                in_burst = True
            elif tick_row[target_process][0] == 'c' and in_burst:
            # in burst
                burst_size += 1
            elif tick_row[target_process][0] != 'c' and in_burst:
            # exited burst
                burst_sizes.append(burst_size)
                burst_size = 0
                in_burst = False
            elif tick_row[target_process][0] != 'c' and not in_burst:
                pass
            else:
                raise Exception('Should not be here')
        burst_sizes.append(burst_size)
        last_estimate = 5
        for burst in burst_sizes:
            last_estimate = (burst + last_estimate)/2
        self.log(JOBSIZE, f"Last estimate {last_estimate}")
        return last_estimate


    # for all processes other than skip_process, we take the local tick offset from the previous tick
    # and add one to it. For the skip_process, we just copy the local tuck offset.
    def update_local_tick_offsets(self, skip_process):
        self.log(LOCAL_TICK, f"Skip Process {skip_process}")
        for index, process in enumerate(self.timeline[self.tick]):
            self.log(LOCAL_TICK,
                     f"Process:{index} state:{process}")
            if process[0] == 'r' and index != skip_process:
                self.log(
                    LOCAL_TICK, f"Process {index} ({process[0]}) needs updated {process[1]}")
                self.log(
                    LOCAL_TICK, f"local {self.timeline[self.tick][index][1]}")

                self.timeline[self.tick][index][1] = self.timeline[self.tick-1][index][1] + 1
            elif process[0] == 'r' and index == skip_process:
                self.timeline[index][self.tick][1] = self.timeline[self.tick-1][index][1]

    def pretty_print_timeline(self):
        for index, entry in enumerate(self.timeline):
            print(f'tick:{index}: {entry}')

    def flatten_chain(self, matrix):
        return list(chain.from_iterable(matrix))
    
    def still_running(self):
        for process in self.timeline[self.tick]:
            if process[0] != 'x':
                return True
        return False


if __name__ == '__main__':
    sjf = SJF('data0.csv')
    sjf.generate_local_timelime()
    sjf.initialize_time_line()
    while sjf.still_running():
        sjf.propose_next_tick()
        sjf.determine_run_text_tick()
    sjf.pretty_print_timeline()
