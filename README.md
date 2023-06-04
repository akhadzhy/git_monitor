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


# TODO