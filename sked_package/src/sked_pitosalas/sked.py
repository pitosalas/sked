from simulation import Simulation
from importlib.metadata import version


import argparse

DOC = """
# Important definitions:

* Simulation variables:
    * Time: Simulation time. Measured in 'tics'. Starts at zero.

* Each process is configured initially with
    * A burst pattern shows the process's state at each tic ("burst_pattern"
        * New: The process has not yet arrived to the scheduler
        * Ready: The process is ready to run
        * Wait: The process is waiting for I/O or other resources
        * Terminated: The process has completed
    * Alternatively a process can be configured with a burst time and total time ("burst" and "total")
        * Total Time: Number of tics the process will run before it terminates
        * Arrival Time: When the process arrives to the scheduler for the first time
    * Alternatively we can probabilistically generate processes using:
        * Burst time: Average number of tics a process will run ("burst")

* Once the simulation starts, each process tracks the following
    * Run Time: Number of CPU tics the process has used so far ("run")
    * Wall Time: Number of tics since the process was first run until it terminates ("wall")
    * Wait Time: Total tics a process spends waiting (on ready queue) ("wait")
    * Waiting Time: Total tics a process spends waiting for I/O or other resources ("waiting")
    * Start Time: Time(tics) when the process was first run ("start")

* When the simulation completes the following are calculated:
* Throughput: Average number of processes completed per tic
* Turnaround: Average number of tics used for a process (1/Througput)
"""

HELP = """
Use this little tool to experiment with and demonstrate different scheduling algorithms. It is open source and a work in progress so expect bugs and help us fix them!
"""


def cli():
    print(f"Welcome! to Sked")
    parser = argparse.ArgumentParser(description='Simple scheduler CLI')

    parser.add_argument('-d', '--doc', action='store_true',
                        help='Print documentation')
    parser.add_argument('-l', '--live', action='store_true', help='Live mode')
    parser.add_argument(
        '-p', '--prompt', action='store_true', help='Prompt mode')
    parser.add_argument('-f', '--file', type=str, help='File path')
    args = parser.parse_args()

    live_mode = args.live
    file_name = args.file
    if (args.doc):
        print(DOC)
        exit(0)
    if (args.prompt and args.live):
        print("Cannot use both prompt and live mode")
        exit(1)
    if (not (args.prompt or args.live)):
        print("Must use either prompt or live mode")
        exit(1)

    s = Simulation()
    s.run(live_mode, file_name)


if __name__ == "__main__":
    cli()
