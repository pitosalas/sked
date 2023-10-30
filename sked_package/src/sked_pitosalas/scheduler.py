from queue import Queue
from abc import ABC, abstractmethod
from pcb import PCB

LOGGING = False
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

    def update_running_process_with_quantum(self):
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
            waiting.waiting_time += 1
        for ready in self.ready_queue._list:
            ready.wait_time += 1
            if ready.start_time is None:
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
        Returns the average time waiting before starting
        """
        total = 0
        for pcb in self.terminated_queue._list:
            total += pcb.start_time if pcb.start_time else 0
        if len(self.terminated_queue._list) == 0:
            return 0
        else:
            return float(total) / len(self.terminated_queue._list)

    def print_queues(self):
        print(f"run: {self.running.pids_string()}, ready: {self.ready_queue.pids_string()}, wait: {self.waiting_queue.pids_string()}, nw: {self.new_queue.pids_string()}, term: {self.terminated_queue.pids_string()}")

    def log(self, fstring: str):
        if LOGGING:
            print(fstring)

    @abstractmethod
    def update(self, time):
        pass


class SJF(Scheduler):
    def __init__(self, sim):
        super().__init__(sim)
        self.sim = sim
        self.print_name = "Shortest Job First"

    def move_based_on_pattern(self, source_queue: Queue, pattern: str, dest_queue: Queue):
        to_move = []
        for pcb in source_queue._list:
            if pcb.get_execution_state(self.sim.clock.get_time()) == pattern:
                to_move += [pcb]
        for pcb in to_move:
            if (dest_queue.name == "Ready Queue"):
                if pcb.start_time is None:
                    pcb.start_time = self.sim.clock.get_time()
            dest_queue.add_at_end(source_queue.remove(pcb))

    def move_to_queue_based_on_execution_state(self, queue):
        self.log(
            f"[move_to_queue_based_on_execution_state] Checking {queue.name} for processes to move")
        to_move_to_ready = []
        to_move_to_waiting = []
        to_move_exit = []
        for pcb in queue._list:
            exec_state = pcb.get_execution_state(self.sim.clock.get_time())
            self.log(f"   checking {pcb.pid}({exec_state}) in {queue}")
            if exec_state == "cpu" and not (queue.name == "Ready Queue" or queue.name == "Running"):
                self.log(f"   moving {pcb.pid} from {queue} to ready queue")
                to_move_to_ready += [pcb]
            elif exec_state == "i/o" and not queue.name == "Waiting Queue":
                self.log(f"   moving {pcb.pid} from {queue} to waiting queue")
                to_move_to_waiting += [pcb]
            elif exec_state == "exit" and not queue.name == "Terminated":
                self.log(f"   moving {pcb.pid} from {queue} to terminated")
                to_move_exit += [pcb]
            elif exec_state == "exit" and not queue.name == "Terminated":
                self.log(f"   moving {pcb.pid} from {queue} to terminated")
                to_move_exit += [pcb]

        for pcb in to_move_to_ready:
            self.ready_queue.add_at_end(queue.remove(pcb))
        for pcb in to_move_to_waiting:
            self.waiting_queue.add_at_end(queue.remove(pcb))
        for pcb in to_move_exit:
            self.terminated_queue.add_at_end(queue.remove(pcb))
        self.log(
            f"   exit")

    def manage_running_process(self):
        running: PCB = self.running.head
        if running is not None:
            running_xstate = running.get_execution_state(
                self.sim.clock.get_time())
            self.log(
                f"[manage_running_process] Checking running process {running.pid}({running_xstate})")
            if running_xstate == "exit":
                self.terminated_queue.add_at_end(self.running.remove(running))
            elif running.get_execution_state(self.sim.clock.get_time()) == "i/o":
                self.waiting_queue.add_at_end(self.running.remove(running))
        if not self.ready_queue.empty() and self.running.empty():
            process_to_run = self.ready_queue.remove_from_front()
            self.log(
                f"  Moving {process_to_run.pid} from ready queue to running")
            self.running.add_at_end(process_to_run)

    def prepare(self, clock):
        self.log(f"[prepare] ***Scheduler Prepare")
        self.move_to_queue_based_on_execution_state(self.new_queue)
        self.move_to_queue_based_on_execution_state(self.waiting_queue)
        self.move_to_queue_based_on_execution_state(self.ready_queue)
        self.manage_running_process()
        self.log(f"[prepare] *** Finished cheduler Prepare")

    def update(self, time):
        self.log(
            f"***[update] Start of scheduler update: {self.simulation.clock.get_time()}")

        self.update_running_process()
        self.update_waiting_processes()

        self.move_to_queue_based_on_execution_state(self.new_queue)
        self.move_to_queue_based_on_execution_state(self.waiting_queue)
        self.move_to_queue_based_on_execution_state(self.ready_queue)
        self.move_to_queue_based_on_execution_state(self.running)
        self.move_to_queue_based_on_execution_state(self.terminated_queue)
        self.manage_running_process()

        self.log(f"***End of update*** {self.simulation.clock.get_time()}")


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

    def update(self):
        self.clock = self.simulation.clock
        self.move_to_ready()
        self.handle_done()
        self.schedule_next()
        self.update_running_process()
        self.update_waiting_processes()


class SJFOld(Scheduler):
    def __init__(self, sim):
        super().__init__(sim)
        self.sim = sim
        self.print_name = "Shortest Job First OLD"

    def update(self):
        self.clock = self.simulation.clock
        self.move_to_ready()
        self.schedule_next()
        self.move_to_terminated()
        self.move_to_waiting()
        self.update_running_process()
        print(f"c: {self.clock.get_time()}, r: {self.running.length()}, rd: {self.ready_queue.length()}, w: {self.waiting_queue.length()}, n: {self.new_queue.length()}, t: {self.terminated_queue.length()}")
        self.update_waiting_processes()

    def schedule_next(self):
        # Get current time
        current_time = self.clock.get_time()

        # Go through all processes on the new queue and check whether their corresponding
        # burst pattern is "ready" at the current time. If so, add them to the end of ready queue.
        self.move_based_on_pattern(self.new_queue, "cpu", self.ready_queue)

        # Check the process in the Running queue. If it's corresponding burst pattern is "terminated",
        # then remove it from the running queue and add it to the terminated queue.
        running = self.running.head
        if running is not None and running.burst_pattern[current_time] == "terminated":
            self.terminated_queue.add_at_end(self.running.remove(running))

        # Check the process on the Running queue. If it's corresponding burst pattern is "wait",
        # then remove it from the running queue and add it to the waiting queue.
        if running is not None and running.burst_pattern[current_time] == "wait":
            self.waiting_queue.add_at_end(self.running.remove(running))

        # Check the processes on the Waiting queue. If it's corresponding burst pattern is "ready",
        # then remove it from the waiting queue and add it to the ready queue
        self.move_based_on_pattern(
            self.waiting_queue, "ready", self.ready_queue)

    def move_based_on_pattern(self, source_queue, pattern, dest_queue):
        to_move = []
        pcb: PCB
        for pcb in source_queue._list:
            if pcb.get_execution_state(self.sim.clock.get_time()) == pattern:
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
