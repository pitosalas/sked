from clock import Clock
import json
from pcb import PCB
from scheduler import FCFS, SJF, RR
import time
from pathlib import Path
import tui
from rich.console import Console
import random
from rich.live import Live

ALLOWED_KEYS = [
    "sched_algorithm", "time_slice", "number_of_processes", "arrival_time", "display",
    "burst_time", "total_time", "auto", "manual", "format", "basic", "burst_pattern",
    "priority", "status", "intro", "PID", "total_time", "arrival_time",
    "burst_time", "priority" "status", "PID", "start_time", "run_time", "wall_time",
    "wait_time", "pid"
]

class Simulation:
    def __init__(self):
        self.clock = Clock()

    def stepper(self, count):
        for i in range(count):
            self.clock.increment()
            if self.sched.all_processes_done():
                break
        tui.print_status(self)

    def run(self, live_mode, file_name):
        self.setup_run(file_name)
        if live_mode:
            self.run_animated()
        else:
            self.run_step()

    def run_animated(self):
        self.intro_rg = tui.generate_intro_rg(self)
        self.run_live()
        tui.print_summary(self)
    
    def run_step(self):
        while not self.sched.all_processes_done():
            response = input("[s(tep),q(uit), g(o): ")
            if response == "q":
                break
            elif response == "s":
                self.stepper(1)
            elif response == "g":
                self.stepper(100)
                break
            else:
                print("Invalid response. Try again.")
        tui.print_summary(self)

    def setup_run(self, given_filename):
        if given_filename:
            filename = given_filename
        else:   
            filename = self.prompt_for_filename()
        full_path = Path("data") / filename
        self.log(f"Running simulation with {full_path}")
        self.import_json_file(full_path)
        self.construct_scheduler()
        self.clock.register_object(self.sched)
        self.configure_scheduler(self.data)
        self.print_intro()
        self.sched.prepare(self.clock)
        tui.print_status(self)

    def run_live(self):
        Console().clear()
        with Live(tui.group_rg(self)) as live:
            while not self.sched.all_processes_done():
                time.sleep(1)  # arbitrary delay
                self.clock.increment()
                live.update(tui.group_rg(self))

    def construct_scheduler(self):
        """
        Constructs the scheduler based on the algorithm specified in the JSON file.
        """
        algo = self.data["sched_algorithm"]
        if algo == "FCFS":
            self.sched = FCFS(self)
        elif algo == "SJF":
            self.sched = SJF(self)
        elif algo == "RR":
            self.sched = RR(self)
        else:
            print("Invalid algorithm. Try again.")

    def prompt_for_filename(self):
        console = Console()
        files = [f.name for f in Path("data").glob("*.json")]
        console.print("[bold]Select a file:[/bold]")
        for i, f in enumerate(files, 1):
            print(f"[{i}] {f}")
        choice = input("Enter your choice: ")
        choice = int(choice) if choice else 1
        return files[choice - 1]

    def print_intro(self):
        console = Console()
        rg = tui.generate_intro_rg(self)
        console.print(rg)

    # Function to read the json file

    def import_json_file(self, filename):
        with open(filename, "r") as f:
            self.data = json.load(f)
            unknown_key = set(self.data)
            if not all(key in ALLOWED_KEYS for key in self.data.keys()):
                print("Error: Invalid JSON file")
                exit()

    def configure_scheduler(self, data):
        self.quantum = data.get("quantum", 1)
        self.sched_algorithm = data["sched_algorithm"]
        self.display = data["display"]

# if there is a key "manual", then we  each process separately.
        for process in data["manual"]:
            pid = process["pid"]
            priority = process.get("priority", None)
            burst_pattern = process.get("burst_pattern", None)
            process = { "pid": pid, "priority": priority, "burst_pattern": burst_pattern}
            self.log(process)
            pcb = PCB(process)
            self.sched.new_queue.add_at_end(pcb)
            self.clock.register_object(pcb)

# if there is a key "auto", then we generate the processes randomly.
        pid = 0
        auto = data.get("auto", None)
        if auto:
            for i in range(auto["number_of_processes"]):
                pid = i + 1
                arrival_time = random.randint(
                    auto["arrival_time"]["from"], auto["arrival_time"]["to"]
                )
                burst_time = random.randint(
                    auto["burst_time"]["from"], auto["burst_time"]["to"]
                )
                total_time = random.randint(
                    auto["total_time"]["from"], auto["total_time"]["to"]
                )
                pcb = PCB(pid, arrival_time, burst_time, total_time)
                self.sched.new_queue.add_at_end(pcb)
                self.clock.register_object(pcb)

    def log(self, fstring: str):
        if False: print(fstring)
