from itertools import chain
import functools

indent = 0


def log(func, arg=0):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        global indent
        print(f"{'   ' * indent} ENTER {func.__name__} {args[0].tick}")
        indent += 1
        # print(f"{args[0].tl_to_string(indent)}")
        value = func(*args, **kwargs)
        indent -= 1
        print(f"{'   ' * indent} EXIT {func.__name__} {args[0].tick}")
        return value
    return wrapper


class SJF:
    def __init__(self, filename: str, nonpreemptive=True):
        self.filename = filename
        self.tick = 0
        self.local_timeline = []
        self.timeline = []
        self.running = None
        self.indent = 0
        self.nonpreemptive = nonpreemptive

    # The file is a csv with 6 columns, corresponding to:
    # wait, burst1, io1, burst2, io2, burst3
    # The local is a list of lists, indexed by process number, and within that indexed by tick

    def generate_local_timelime(self):
        with open(self.filename, "r") as f:
            for line in f:
                process_lt = self.process_lt(line)
                self.local_timeline.append(process_lt)

    def process_lt(self, line):
        process_lt = []
        line_split = line.split(",")
        process_lt.append(int(line_split[0]) * ["-"])
        process_lt.append(int(line_split[1]) * ["r"])
        process_lt.append(int(line_split[2]) * ["i"])
        process_lt.append(int(line_split[3]) * ["r"])
        process_lt.append(int(line_split[4]) * ["i"])
        process_lt.append(int(line_split[5]) * ["r"])
        process_lt = self.flatten_chain(process_lt)
        return process_lt

    def initialize_time_line(self):
        first_entry = []
        any_cpu = False
        for index, process in enumerate(self.local_timeline):
            if process[0] == "r" and not any_cpu:
                any_cpu = True
                first_entry.append(["c", 0])
            elif process[0] == "r" and any_cpu:
                first_entry.append(["r", 1])
            else:
                first_entry.append([process[0], 0])
        self.timeline.append(first_entry)

    def propose_next_tick(self):
        new_entry = []
        for index, local_state in enumerate(self.local_timeline):
            new_entry.append(
                [
                    self.get_local_state(index, self.tick),
                    self.timeline[self.tick - 1][index][1],
                ]
            )
        self.timeline.append(new_entry)

    def get_local_state(self, process, tick):
        local_state = None
        prev_tick_offset_to_local = self.timeline[tick - 1][process][1]
        if (
            len(self.local_timeline[process])
            <= tick - self.timeline[tick - 1][process][1]
        ):
            local_state = "x"
        else:
            local_state = self.local_timeline[process][
                tick - self.timeline[tick - 1][process][1]
            ]
        return local_state

    def determine_run_text_tick(self):
        if (
            self.running is not None
            and self.timeline[self.tick][self.running][0] == "r"
            and self.nonpreemptive
        ):
            # raise Exception('Should not be here')
            self.update_local_tick_offsets(self.running)
        else:
            try_running = None
            estimated_size = 100
            current_tick = self.timeline[self.tick]
            for index, process in enumerate(current_tick):
                if (
                    process[0] == "r"
                    and self.job_size(current_tick, index) < estimated_size
                ):
                    try_running = index
                    estimated_size = self.job_size(current_tick, index)
            if try_running is not None:
                self.running = try_running
                self.timeline[self.tick][try_running][0] = "c"
                self.timeline[self.tick][try_running][1] = self.timeline[self.tick - 1][
                    try_running
                ][1]
                self.update_local_tick_offsets(try_running)

    def job_size(self, current_tick, target_process):
        burst_size = 0
        in_burst = False
        burst_sizes = []
        for tick_row in self.timeline[:-1]:
            if tick_row[target_process][0] == "c" and not in_burst:
                # entered burst
                burst_size += 1
                in_burst = True
            elif tick_row[target_process][0] == "c" and in_burst:
                # in burst
                burst_size += 1
            elif tick_row[target_process][0] != "c" and in_burst:
                # exited burst
                burst_sizes.append(burst_size)
                burst_size = 0
                in_burst = False
            elif tick_row[target_process][0] != "c" and not in_burst:
                pass
            else:
                raise Exception("Should not be here")
        last_estimate = 5
        if in_burst:
            burst_sizes.append(burst_size)
        for burst in burst_sizes:
            last_estimate = (burst + last_estimate) / 2
        return last_estimate

    # for all processes other than skip_process, we take the local tick
    # offset from the previous tick and add one to it. For the skip_process
    # we just copy the local tuck offset.

    def update_local_tick_offsets(self, skip_process):
        for index, process in enumerate(self.timeline[self.tick]):
            if process[0] == "r" and index != skip_process:
                self.timeline[self.tick][index][1] = (
                    self.timeline[self.tick - 1][index][1] + 1
                )
            elif process[0] == "c" and index != skip_process:
                new_local_tick = self.timeline[self.tick - 1][index][1]
                if new_local_tick > 0:
                    self.timeline[self.tick][index][1] = new_local_tick
            elif process[0] == "r" and index == skip_process:
                self.timeline[self.tick][index][0] = "c"
                self.timeline[self.tick][index][1] = self.timeline[self.tick - 1][
                    index
                ][1]
            elif process[0] == "c" and index == skip_process:
                new_local_tick = self.timeline[self.tick - 1][index][1]
                if new_local_tick > 0:
                    self.timeline[self.tick][index][1] = new_local_tick

    def pretty_print_local_timeline(self):
        print("LOCAL TIMELINE")
        for index, entry in enumerate(self.local_timeline):
            print(f'process:{index}: {(" ").join(entry)}')
        print()

    def pretty_print_timeline(self):
        print("TIMELINE:")
        print(self.tl_to_string())

    def tl_to_string(self, indent=0):
        out = ""
        for index, entry in enumerate(self.timeline):
            out += f"{'   ' * indent}tick:{index}: {entry}\n"
        return out

    def compressed_tl(self):
        out = ""
        for index, entry in enumerate(self.timeline):
            out += f"tick:{index}({self.compressed_tl_process(index, entry)})."
        return out

    def compressed_tl_process(self, index, tl_process):
        out = ""
        for proc, procarray in enumerate(tl_process):
            out += f"p{proc}({procarray[0]}{procarray[1]})."
        return out

    def flatten_chain(self, matrix):
        return list(chain.from_iterable(matrix))

    def still_running(self):
        curr_tick = self.timeline[self.tick]
        for process in curr_tick:
            if process[0] != "x":
                return True
        return False

    def print_running_sequence(self):
        print("\n**** RUNNING SEQUENCE\n")
        for tick, tick_data in enumerate(self.timeline):
            running = None
            for process, process_data in enumerate(tick_data):
                if process_data[0] == "c" and running is None:
                    running = process
                    print(f"Tick {tick}: Process {process} runs.")
                elif process_data[0] == "c" and running != None:
                    print(
                        f"Bug at tick {tick}: Process {process} wants to run, but process {running} is already running."
                    )
            if running is None:
                print(f"Tick {tick}: No Process is running")

    def print_statistics(self):
        print("     Statistics")
        wait_time = [0, 0, 0]
        for tick, tick_data in enumerate(self.timeline):
            for process, process_data in enumerate(tick_data):
                if process_data[0] == "r":
                    wait_time[process] += 1
        print(f"     Waiting time for each Process: {wait_time}")

    def run(self):
        self.generate_local_timelime()
        self.initialize_time_line()
        self.pretty_print_local_timeline()
        while self.still_running():
            self.tick += 1
            self.propose_next_tick()
            self.determine_run_text_tick()
        self.pretty_print_timeline()
        self.print_running_sequence()
        self.print_statistics()


if __name__ == "__main__":
    from pathlib import Path

    # files = [f.name for f in Path(".").glob("*.csv")]
    files = ["jesse_levinson.csv"]
    for i, f in enumerate(files):
        print(f"\n**** File Name: {f}")
        print(f"     Non Preemptive")
        sjf = SJF(f, True)
        sjf.run()
        print(f"     Preemptive")
        sjf = SJF(f, False)
        sjf.run()
