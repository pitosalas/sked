from rich import print
from rich.console import Group
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.console import Console
from rich.prompt import Prompt
from rich.live import Live
from rich import box

# Mapping format strings to column headers

COLUMN_HEADERS = {
      "pid": "PID",
      "total_ime": "Total Time",
      "arrival_time": "Arrival Time",
      "burst_time": "Burst Time",
      "priority": "Priority",
      "start_time": "Start Time",
      "total_time": "Total Time",
      "run_time": "Run Time",
      "wall_time": "Wall Time",
      "wait_time": "Wait Time",
      "waiting_time": "Waiting Time",
      "status": "Status",
       "burst_pattern": "Burst Pattern"
}

def generate_intro_rg(sim):
    line1 = Text(f"Algorithm: {sim.sched.print_name}", style="bold red")
    table = Table(show_header=True,
                  header_style="bold magenta")
    add_columns(table, sim.display["intro"])
    add_rows(table, sim.sched.new_queue, sim.display["intro"])
    return Group(line1, table)

def print_status(sim) -> None:
    rg = generate_status_rg(sim)
    console = Console()
    console.print(rg)
    sim.sched.print_queues()


def generate_status_rg(sim) -> Group:
    """
    Prints the current status of the operating system representing the terminated queue.
    """
    line1 = Text(f"Clock: {sim.clock.get_time()}", style="bold red")
    line2 = Text(f"Timeline+: {sim.sched.progress}", style="bold red")
    table = Table(show_header=True, header_style="bold magenta")
    add_columns(table, sim.display["status"])
    add_rows(table, sim.sched.running, sim.display["status"])
    add_rows(table, sim.sched.ready_queue, sim.display["status"])
    add_rows(table, sim.sched.waiting_queue, sim.display["status"])
    add_rows(table, sim.sched.terminated_queue, sim.display["status"])
    add_rows(table, sim.sched.new_queue, sim.display["status"])
    return Group(line1, line2, table)

def add_rows(table, queue, columns):
    for pcb in queue._list:
        row = []
        for column in columns:
            value = getattr(pcb, column)
            row.append(str(value))
        table.add_row(*row)

def add_columns(table, columns):
    for column in columns:
        table.add_column(COLUMN_HEADERS[column], justify="right")


def print_summary(sim) -> None:
    rg = generate_summary_rg(sim)
    console = Console()
    console.print(rg)

def generate_summary_rg(sim):
    """
    Prints the summary of the operating system representing the terminated queue.
    """
    line1 = Text(f"Clock: {sim.clock.get_time()}", style="bold red")
    line2 = Text(
        f"Average Time spent Waiting: {sim.sched.get_average_wait_time()}", style="bold red")
    line3 = Text(
        f"Average waiting before starting: {sim.sched.get_average_start_time()}", style="bold red")
    return Group(line1, line2, line3)


def group_rg(sim):
    status_rg = generate_status_rg(sim)
    return Group(sim.intro_rg, status_rg)

