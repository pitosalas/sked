class PCB:
    """
    Process Control Block (PCB) class represents a process in the operating system.
    It contains information about the process such as its process ID (pid), arrival time,
    burst time, priority, and completion time.
    """

    def __init__(self, args):
        self.pid: str = args["pid"]
        self.arrival_time: int = args.get("arrival_time", 0)
        self.burst_time = args.get("burst_time", None)
        self.burst_pattern = args.get("burst_pattern", None)
        self.priority: int = args.get("priority", 0)
        self.total_time = args.get("total_time", 0)
        self.start_time = None
        self.run_time = 0
        self.wall_time: int = None
        self.wait_time = 0
        self.waiting_time = 0
        self.status = "New"

    def update(self, time: int) -> None:
        """
        Updates the PCB's wall time to the given time if the PCB is not in the New or Terminated state.
        """
        if self.status not in ("New", "Terminated"):
            self.wall_time = time

# Retrieve the current run/wait status of the process. The burst pattern shows the execution
# state by tick, assuming that the process never had to wait. While the process is waiting, the
# process is not advancing in the burst pattern. The wait time is the number of ticks the process
# has been in the ready queue, not running.

    def get_execution_state(self) -> str:
        if self.burst_pattern is None:
            return None
        if self.wall_time is None and self.burst_pattern[0] == "ready":
            self.wall_time = 0
            return "ready"
        else:
            return self.burst_pattern[self.wall_time-self.wait_time]

    def __repr__(self):
        return f"PCB({self.pid}, {self.arrival_time}, {self.burst_time}, {self.total_time}, {self.wait_time})"
