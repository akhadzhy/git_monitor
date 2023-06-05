import os
import time
import logging
import atexit
from git import Repo
from queue import Queue
from threading import Thread
from subprocess import Popen


class GitMonitor:
    def __init__(
            self, 
            repo_dir: str,
            test_script: str,
            branch: str,
            ssh_key_path: str,
            max_concurrent_tasks: int = 3,
            sleep_duration: int = 5
        ) -> None:
        # Set the GIT_SSH_COMMAND with path to your private key
        os.environ['GIT_SSH_COMMAND'] = f"ssh -i {ssh_key_path}"

        if not os.path.isdir(repo_dir):
            raise NotADirectoryError(f"The provided repository directory '{repo_dir}' does not exist.")

        if not os.path.isfile(test_script):
            raise FileNotFoundError(f"The provided test script file '{test_script}' does not exist.")
        
        self.repo_dir: str  = repo_dir
        self.test_script: str = test_script
        self.branch: str = branch

        # Initialize Repo and check if the branch exists
        self.repo: Repo = Repo(repo_dir)
        
        if branch not in self.repo.branches:
            raise ValueError(f"The provided branch '{branch}' does not exist in the repository.")

        if 'origin' not in self.repo.branches:
            raise ValueError(f"The remotes origin branch does not exist in the repository.")
        
        self.changed_files: Queue = Queue()
        self.running_tasks: dict[str, Popen] = {}
        self.MAX_CONCURRENT_TASKS: int = max_concurrent_tasks
        self.SLEEP_DURATION_M: int = sleep_duration

    def cleanup(self) -> None:
        """Terminates any running tasks upon program exit"""
        for file, process in list(self.running_tasks.items()):
            try:
                process.terminate()
                logging.info(f"Cleaned up task for file: {file}")
            except Exception as e:
                logging.error(f"Failed to clean up task for file: {file}. Error: {e}")

    def update_checker(self) -> None:
        """Continuously checks for updates in the Git repository"""
        while True:
            try:
                # Pull the latest changes
                current = self.repo.head.commit
                self.repo.git.checkout(self.branch)
                self.repo.remotes.origin.pull()
                logging.info("Repository updated successfully.")

                # If the commit ID changed, queue the changed files
                if current != self.repo.head.commit:
                    # Get the names of the changed files
                    diff_index = current.diff(self.repo.head.commit)
                    new_changed_files = [item.a_path for item in diff_index]

                    for file in new_changed_files:
                        self.changed_files.put(file)
                        logging.info(f"New change detected in file: {file}")

                # Sleep for N minutes
                time.sleep(self.SLEEP_DURATION_M * 60)
            except Exception as e:
                logging.error(f"Exception occurred in update_checker: {e}")

    def task_controller(self) -> None:
        """Controls the execution of test tasks"""
        while True:
            try:
                # checking running_tasks on completion or fail
                for file, process in list(self.running_tasks.items()):
                    result, error = process.communicate()

                    # Handle completed tasks
                    if process.poll() is not None:
                        del self.running_tasks[file]
                        if process.returncode != 0:
                            logging.error(f"Test failed for file: {file}. Error: {error}")
                        else:
                            logging.info(f"Test completed for file: {file}. Result: {result}")

                    # Handle file updates during task execution
                    elif file in list(self.changed_files.queue):
                        process.terminate()
                        del self.running_tasks[file]
                        self.task_runner(file)

                # check if there is free slot to run a task
                if len(self.running_tasks) < self.MAX_CONCURRENT_TASKS:
                    self.task_runner(self.changed_files.get())

                time.sleep(1)
            except Exception as e:
                logging.error(f"Exception occurred in task_controller: {e}")

    def task_runner(self, file: str) -> None:
        """Starts a new test task"""
        try:
            process = Popen(['python', self.test_script, file])
            self.running_tasks[file] = process
            logging.info(f"Test started for file: {file}")
        except Exception as e:
            logging.error(f"Exception occurred in task_runner: {e}")


if __name__ == "__main__":
    # Set up logging with timestamps
    logging.basicConfig(
        filename='test_runner.log',
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    git_monitor = GitMonitor(
        repo_dir='./tests/mock_repo',
        test_script='./tests/mock_repo/mock_file.py',
        branch='main',
        ssh_key_path='path/to/your/private/key',
    )

    # Register cleanup function
    atexit.register(git_monitor.cleanup)

    # Start the update checker and task controller threads
    Thread(target=git_monitor.update_checker).start()
    Thread(target=git_monitor.task_controller).start()
