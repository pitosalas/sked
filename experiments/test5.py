from rich import print
from pathlib import Path

files = [f.name for f in Path('.').glob('*.json')]

print("[bold]Select a file:[/bold]")
for i, f in enumerate(files, 1):
    print(f"[{i}] {f}")
    
choice = int(input("Enter your choice: ", default=1))
selected_file = files[choice-1]

print(f"[green]You selected: {selected_file}[/green]")