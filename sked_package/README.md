# sked.py

# Developing

sked/ contains the python packate in sked_pitosalas as well as other files that were used to assist development
sked/sked_pitosalas contains the code that will turn into the package uploaded to pypi
sked/sked_pitosalas/pyproject.toml is where the package is configured

# Distributing


* Increment version number in pyproject.toml
```
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=mytoken 

python3 -m build
python3 -m twine upload --repository testpypi dist/* 
python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps -U sked_pitosalas
pyenv rehash

# or
python3 -m build; python3 -m twine upload --skip-existing --repository testpypi dist/* ; python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps -U sked_pitosalas; pyenv rehash

# Run configuration .json files
## Top Level Keys
    * "sched_algorithm" -> "RR", "SJF", "FCFS"
    * "display" -> See below
    * "manual" -> See below
    * "auto" -> See below
    * "log" -> "on" or "off"

## "display" 

* Contains two keys, "intro" and "status"
* Each configures the columns that are displayed
* Each contains a list of values, from the list:
    * "pid" - process id
    * "burst_pattern" - See below
    * "status" - "Ready Queue", "Waiting queue", "running", "terminated"s
    * "start_time"
    * "run_time" - ßß
    * "wall_time" - 
    * "wait_time" - How long the thread spends in the ready queue
    * "waiting_time" - Total amount of time in the ready and wait queues

## "auto"

## manual

## Exanple
```json
{
  "sched_algorithm": "SJF",
  "display": {
    "intro": [
      "pid",
      "burst_pattern"
    ],
    "status": [
      "pid",
      "status",
      "start_time",
      "run_time",
      "wall_time",
      "wait_time",
      "waiting_time"
    ]
  },
  "manual": [
    {
      "pid": "p1",
      "burst_pattern": [
        "cpu",
        "cpu",
        "cpu",
        "exit"
      ]
    },
    {
      "pid": "p2",
      "burst_pattern": [
        "new",
        "i/o",
        "cpu",
        "exit"
      ]
    }
  ]
}
```
