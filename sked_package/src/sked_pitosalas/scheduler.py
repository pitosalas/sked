from queue import Queue
from abc import ABC, abstractmethod
from rich.live import Live


class Scheduler(ABC):
    def __init__(self, sim):
        self.new_queue = Queue("New", sim)
        self.ready_queue: Queue = Queue("Ready Queue", sim)
        self.waiting_queue: Queue = Queue("Waiting Queue", sim)
        self.terminated_queue: Queue = Queue("Terminated", sim)
        self.running: Queue = Queue("Running", sim)
        self.simulation = sim
        self.progress = ""
        self.print_name = ""
    

    def all_processes_done(self):
        """
        Returns True if all processes are done, False otherwise.
        """
        return self.new_queue.empty() and self.ready_queue.empty() and self.waiting_queue.empty() and self.running.empty()

    def quantum_elapsed(self):
        """
        Returns True if quantum has elapsed, False otherwise.
        """
        time = self.simulation.clock.get_time()
        return time != 0 and time % self.simulation.quantum == 0

    def move_to_ready(self):
        # while there are still pcbs on new queue, remove them from new queue and add them to ready queue
        to_move = []
        for pcb in self.new_queue._list:
            if pcb.arrival_time <= self.clock.get_time():
                to_move += [pcb]
        for pcb in to_move:
            pcb.wall_time = self.clock.get_time()
            self.ready_queue.add_at_end(self.new_queue.remove(pcb))

    def handle_done(self):
        # if there is a running process, check if it is done
        current_process = self.running.head
        if current_process is not None and current_process.run_time >= current_process.total_time:
            # if it is done, add it to the terminated queue and set running to None
            self.terminated_queue.add_at_end(
                self.running.remove(current_process))

    def schedule_next(self):
        # Return if no one to run
        if not self.running.empty() or self.ready_queue.empty():
            return
        process_to_run = self.ready_queue.remove_from_front()
        self.running.add_at_end(process_to_run)

    def __repr__(self):
        return "Scheduler({clock})"

    def update_running_process(self):
        # if there is a running process, increment its time
        running = self.running.head
        if running is None:
            return
        running.run_time += 1
        if running.start_time is None:
            running.start_time = self.clock.get_time()
        self.progress += f"{running.pid}|"

    def update_running_process_with_preemption(self):
        # if quantum has elapsed
        if self.quantum_elapsed():
            # if there is a running process, check if it is done
            current_process = self.running.head
            if current_process is not None:
                self.ready_queue.add_at_end(
                    self.running.remove(current_process))
        self.update_running_process(self)

    def update_waiting_processes(self):
        for waiting in self.waiting_queue._list:
            waiting.wait_time += 1
            waiting.waiting_time += 1
        for ready in self.ready_queue._list:
            ready.wait_time += 1
            ready.waiting_time += 1
            if ready.start_time is not None:
                ready.start_time = self.clock.get_time()

    def get_average_wait_time(self):
        """
        Returns the average wait time of all processes.
        """
        total = 0
        for pcb in self.terminated_queue._list:
            total += pcb.wait_time
        if len(self.terminated_queue._list) == 0:
            return 0
        else:
            return float(total) / len(self.terminated_queue._list)

    def get_average_start_time(self):
        """
        Returns the average time waiting  before starting
        """
        total = 0
        for pcb in self.terminated_queue._list:
            total += pcb.start_time if pcb.start_time else 0
        if len(self.terminated_queue._list) == 0:
            return 0
        else:
            return float(total) / len(self.terminated_queue._list)

    @abstractmethod
    def update(self, time):
        pass


class SJF(Scheduler):
    def __init__(self, sim):
        super().__init__(sim)
        self.sim = sim
        self.print_name = "Shortest Job First"

    def update(self, time):
        self.clock = self.simulation.clock
        self.move_to_ready()
        self.schedule_next()
        self.move_to_terminated()
        self.move_to_waiting()
        self.update_running_process()       
        print(f"c: {time}, r: {self.running.length()}, rd: {self.ready_queue.length()}, w: {self.waiting_queue.length()}, n: {self.new_queue.length()}, t: {self.terminated_queue.length()}")
        self.update_waiting_processes()

    def move_based_on_pattern(self, source_queue, pattern, dest_queue):
        to_move = []
        for pcb in source_queue._list:
            if pcb.burst_pattern[self.clock.get_time()] == pattern:
                to_move += [pcb]
        for pcb in to_move:
            if (dest_queue.name == "Ready Queue"):
                if pcb.start_time is None:
                    pcb.start_time = self.clock.get_time()
            dest_queue.add_at_end(source_queue.remove(pcb))

    def move_to_ready(self):
        # while there are still pcbs on new queue, remove them from new queue and add them to ready queue
        self.move_based_on_pattern(self.new_queue, "ready", self.ready_queue)
        self.move_based_on_pattern(
            self.waiting_queue, "ready", self.ready_queue)
        self.move_based_on_pattern(self.running, "ready", self.ready_queue)

    def move_to_waiting(self):
        self.move_based_on_pattern(self.new_queue, "wait", self.waiting_queue)
        self.move_based_on_pattern(
            self.ready_queue, "wait", self.waiting_queue)
        self.move_based_on_pattern(self.running, "wait", self.waiting_queue)

    def move_to_terminated(self):
        self.move_based_on_pattern(
            self.new_queue, "terminated", self.terminated_queue)
        self.move_based_on_pattern(
            self.ready_queue, "terminated", self.terminated_queue)
        self.move_based_on_pattern(
            self.running, "terminated", self.terminated_queue)
        self.move_based_on_pattern(
            self.waiting_queue, "terminated", self.terminated_queue)

class RR(Scheduler):
    def __init__(self, sim):
        super().__init__(sim)
        self.sim = sim
        self.print_name = "Round Robin"

    def update(self, time):
        self.clock = self.simulation.clock
        if (self.quantum_elapsed()):
            self.progress += f"*"
            # move running process to end of ready queue
            current_process = self.running.head
            if current_process is not None:
                self.ready_queue.add_at_end(
                    self.running.remove(current_process))
        self.move_to_ready()
        self.handle_done()
        self.schedule_next()
        self.update_running_process()
        self.update_waiting_processes()


class FCFS(Scheduler):
    def __init__(self, sim):
        super().__init__(sim)
        self.sim = sim
        self.print_name = "First Come First Serve"

    def update(self, time):
        self.clock = self.simulation.clock
        self.move_to_ready()
        self.handle_done()
        self.schedule_next()
        self.update_running_process()
        self.update_waiting_processes()
