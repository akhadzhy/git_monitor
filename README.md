# GitMonitor

GitMonitor is a tool that continuously monitors a Git repository for changes and automatically runs a specified script for each changed file in the repository. It's designed to be used in scenarios where continuous testing or update of files is required whenever there are changes in a Git repository.

## Features

- Continuously monitors a specified Git repository for changes.
- Automatically runs a specified script for each changed file in the repository.
- Handles a specified number of tasks concurrently.
- Cleans up running tasks on program exit.

## Dependencies

- Python 3.x
- GitPython
- Git (command line tool)

## Setup

1. Install Python 3.x
2. Install the required Python modules with pip:

```bash
pip install gitpython
```bash

## GitMonitor Working Process

Here's a simplified overview of how `GitMonitor` works:

1. **Initialization**: Create a `GitMonitor` instance with a Git repository directory, test script, branch name, ssh key path, and optionally, maximum concurrent tasks and sleep duration.

2. **Continuous Monitoring**: The `update_checker` and `task_controller` methods run continuously on separate threads. 

   - `update_checker`: It checks for updates in the Git repository at regular intervals (determined by `SLEEP_DURATION_M`). If new changes are found in the specified branch, the changed file paths are added to a queue (`changed_files`).

   - `task_controller`: It manages the execution of test tasks. It checks if there are free slots to start new tasks (based on `MAX_CONCURRENT_TASKS`) and whether there are tasks that have finished running. If a file update occurs during a task execution, it terminates the task and re-queues it.

3. **Task Execution**: When `task_controller` starts a new task, it calls `task_runner`. `task_runner` runs the test script with the file as an argument in a separate process and adds it to a dictionary of running tasks (`running_tasks`).

4. **Cleanup**: When the program is about to exit, `cleanup` method is invoked which terminates any running tasks.
