import time

from rich.live import Live
from rich.table import Table
from rich import print
from rich.console import Group
from rich.panel import Panel
from rich.text import Text



def generate_live(count):
    table1 = Table()
    table1.add_column("Row ID")
    table1.add_column("Description")
    table1.add_column("Level")
    for row in range(12):
        if count < 5:
            table1.add_row(f"{row}", f"description {row}", "[red]ERROR")
        else:
            table1.add_row(f"{row*100}", f"description {row}", "[green]GOOD")


    table2 = Text(f"Algorithm: {count}", style="bold red")
    table0 = Text(f"Algorithm: xxx", style="bold red")
    table3 = Text(f"Algorithm: xxx", style="bold red")
    return(Group(table0, table1, table2, table3))

count = 0
with Live(generate_live(count), refresh_per_second=4) as live:
    for row in range(12):
        time.sleep(0.4)  # arbitrary delay
        # update the renderable internally
        count += 1
        live.update(generate_live(count))
