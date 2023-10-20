from itertools import chain

PROCESS_IT = 0
FIRST_TIME = 1
NEXT_TICK = 2
LOCAL_TICK = 3
JOBSIZE = 4
MAINLOOP = 5
LOGGING = [False, False, True, True, False, False]


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
        self.log(FIRST_TIME, f"     Local timeline:{self.local_timeline}")
        for index, process in enumerate(self.local_timeline):
            first_entry.append([process[0], 0])
            self.log(FIRST_TIME, first_entry)
        self.timeline.append(first_entry)
        self.log(FIRST_TIME, "*** end of first time init***")

    def propose_next_tick(self):
        self.log(
            NEXT_TICK, f"*** ENTER propose_next_tick at @{self.tick}")

        self.tick += 1
        tick = self.tick  # just for convenience
        # first calculate it without regard to the fact that only one process can run at a time
        new_entry = []
        for index, local_state in enumerate(self.local_timeline):
            self.log(
                NEXT_TICK, f"    Propose next process: {index} state:{self.get_local_state(index, tick)}")
            if self.get_local_state(index, tick) == 'c':
                new_entry.append(['r', 0])
            elif self.get_local_state(index, tick) == 'i':
                new_entry.append(['i', 0])
            elif self.get_local_state(index, tick) == '-':
                new_entry.append(['-', 0])
            elif self.get_local_state(index, tick) == 'x':
                new_entry.append(['x', 0])
            else:
                raise Exception('     Should not be here')
        self.timeline.append(new_entry)
        self.log(
            NEXT_TICK, f"*** EXIT propose_next_tick at tick({self.tick}) adding: {new_entry} (timeline length {len(self.timeline)}")

    def get_local_state(self, process, tick):
        local_state = None
        self.log(
            NEXT_TICK, f"*** ENTER get_local_state #{process} @{tick}")
        if len(self.local_timeline[process]) <= tick-self.timeline[tick-1][process][1]:
            self.log(
                NEXT_TICK, f"     len_timeline: {len(self.local_timeline[process])}, @{tick}, offset: {self.timeline[tick-1][process][1]}")
            local_state = 'x'
        else:
            local_state = self.local_timeline[process][tick -
                                                       self.timeline[tick-1][process][1]]
        self.log(
            NEXT_TICK, f"*** EXIT get_local_state #{process} @{tick} returning state: {local_state}")
        return local_state

    def determine_run_text_tick(self):
        self.log(NEXT_TICK, f"*** ENTER determine_run_text_tick @{self.tick}")
        if self.running is not None and self.timeline[self.tick][self.running][0] == 'c':
            self.log(
                NEXT_TICK, f'     process {self.running} continues running')
            self.update_local_tick_offsets(self.running)
        else:
            try_running = None
            estimated_size = -1
            current_tick = self.timeline[self.tick]
            self.log(NEXT_TICK, f"     current_tick: {current_tick}")

            for index, process in enumerate(current_tick):
                self.log(NEXT_TICK, f"     Process:{index} state: {process}")
                if process[0] == 'r':
                    if try_running is None:
                        try_running = index
                    elif self.job_size(current_tick, index) < estimated_size:
                        try_running = index
                        estimated_size = self.job_size(current_tick, index)
            if try_running is not None:
                self.log(
                    NEXT_TICK, f'     Process {try_running} begins running')
                self.running = try_running
                self.timeline[self.tick][try_running][0] = 'c'
                self.update_local_tick_offsets(try_running)
        self.log(NEXT_TICK, "*** EXIT determine_run_text_tick")

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
        self.log(
            JOBSIZE, f"Job Size for {target_process} during tick {self.tick} is {last_estimate}")
        return last_estimate

    # for all processes other than skip_process, we take the local tick
    # offset from the previous tick and add one to it. For the skip_process
    # we just copy the local tuck offset.

    def update_local_tick_offsets(self, skip_process):
        self.log(
            LOCAL_TICK, f"\n*** ENTER Update_local_tick_offsets tick:{self.tick} process:{skip_process}")
        for index, process in enumerate(self.timeline[self.tick]):
            self.log(LOCAL_TICK,
                     f"      Process:{index} state:{process}")
            if process[0] == 'r' and index != skip_process:
                self.log(
                    LOCAL_TICK, f"      Process {index} ({process[0]}) has local offset:{process[1]} local {self.timeline[self.tick][index][1]}")
                self.timeline[self.tick][index][1] = self.timeline[self.tick-1][index][1] + 1
            elif process[0] == 'c' and index != skip_process:
                new_local_tick = self.timeline[self.tick-1][index][1] - 1
                if new_local_tick > 0:
                    self.timeline[self.tick][index][1] = new_local_tick
            elif process[0] == 'r' and index == skip_process:
                self.timeline[index][self.tick][1] = self.timeline[self.tick-1][index][1]
            elif process[0] == 'c' and index == skip_process:
                new_local_tick = self.timeline[self.tick-1][index][1] - 1
                if new_local_tick > 0:
                    self.timeline[self.tick][index][1] = new_local_tick
            else:
                self.log(LOCAL_TICK, "      Unexpected: No match")
        self.log(
            LOCAL_TICK, f"\n*** EXIT Update_local_tick_offsets tick:{self.tick}")

    def pretty_print_timeline(self):
        print("** Timeline:")
        for index, entry in enumerate(self.timeline):
            print(f'tick:{index}: {entry}')

    def pretty_print_local_timeline(self):
        print("** Local Timeline:")
        for index, entry in enumerate(self.local_timeline):
            print(f'process:{index}: {(" ").join(entry)}')
        print()

    def flatten_chain(self, matrix):
        return list(chain.from_iterable(matrix))

    def still_running(self):
        max_tick = -1
        for process in self.local_timeline:
            self.log(MAINLOOP, len(process))
            if len(process) > max_tick:
                max_tick = len(process)
        self.log(MAINLOOP, f"{self.tick}, {max_tick}")
        return self.tick < max_tick


if __name__ == '__main__':
    sjf = SJF('debbie.csv')
    sjf.generate_local_timelime()
    sjf.initialize_time_line()
    sjf.pretty_print_local_timeline()
    while sjf.still_running():
        sjf.propose_next_tick()
        sjf.determine_run_text_tick()
    sjf.pretty_print_timeline()
