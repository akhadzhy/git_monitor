import unittest
from unittest.mock import patch, Mock
from queue import Queue
from git import Repo
from git_monitor import GitMonitor
from subprocess import Popen

class TestGitMonitor(unittest.TestCase):

    # Using decorators to patch os.environ and Repo.__init__, mocking their behavior.
    @patch('os.path.isdir')
    @patch('os.path.isfile')
    @patch('os.environ')
    @patch('agit_guard.Repo', autospec=True) 
    def test_init(self, mock_repo_init, mock_env, mock_isfile, mock_isdir):
        # Set up mocks
        mock_repo_init.return_value = None
        mock_isfile.return_value = True
        mock_isdir.return_value = True

        # Mock a git Repo object with a branch
        mock_repo = Mock()
        mock_repo.branches = ['main']
        mock_repo_init.return_value = mock_repo

        REPO_DIR = './tests/mock_repo'
        TEST_SCRIPT = f'{REPO_DIR}/mock_file.py'

        # Create an instance of GitMonitor with the given parameters. The mocked objects will be used here.
        gm = GitMonitor(
                repo_dir=REPO_DIR,
                test_script=TEST_SCRIPT,
                branch='main',
                ssh_key_path='path/to/your/private/key',
            )


        # Check that os.environ.__setitem__ was called once with the right parameters.
        mock_env.__setitem__.assert_called_once_with('GIT_SSH_COMMAND', 'ssh -i path/to/your/private/key')

        # Check that Repo.__init__ was called once with the right parameter.
        mock_repo_init.assert_called_once_with('./tests/mock_repo')

        # Check that the instance variables of GitMonitor are set correctly.
        self.assertEqual(gm.repo_dir, REPO_DIR)
        self.assertEqual(gm.test_script, TEST_SCRIPT)
        self.assertEqual(gm.branch, 'main')

        # Check that changed_files and running_tasks are instances of the correct classes.
        self.assertIsInstance(gm.changed_files, Queue)
        self.assertIsInstance(gm.running_tasks, dict)

        # Check that the instance variables are set to their default values correctly.
        self.assertEqual(gm.MAX_CONCURRENT_TASKS, 3)
        self.assertEqual(gm.SLEEP_DURATION_M, 5)

        # Check the calls to os.path.isfile and os.path.isdir
        mock_isfile.assert_called_once_with(TEST_SCRIPT)
        mock_isdir.assert_called_once_with(REPO_DIR)

    @patch.object(GitMonitor, 'cleanup')
    def test_cleanup(self, mock_cleanup):
        # Add test body here
        pass

    @patch.object(GitMonitor, 'update_checker')
    def test_update_checker(self, mock_update_checker):
        # Add test body here
        pass

    @patch.object(GitMonitor, 'task_controller')
    def test_task_controller(self, mock_task_controller):
        # Add test body here
        pass

    @patch.object(GitMonitor, 'task_runner')
    def test_task_runner(self, mock_task_runner):
        # Create a mock process object to return from Popen
        mock_process = Mock()
        mock_task_runner.return_value = mock_process

        REPO_DIR = './tests/mock_repo'
        TEST_SCRIPT = f'{REPO_DIR}/mock_file.py'

        # Create a GitMonitor instance
        gm = GitMonitor(
            repo_dir=REPO_DIR,
            test_script=TEST_SCRIPT,
            branch='main',
            ssh_key_path='path/to/your/private/key',
        )

        # Mock a file for the task runner
        mock_file = "changed"

        # Call task_runner
        gm.task_runner(mock_file)

        # Check that Popen was called with the correct parameters
        mock_task_runner.assert_called_once_with(['python', TEST_SCRIPT, 'changed'])

        # Check that the process was stored in running_tasks
        self.assertIn(mock_file, gm.running_tasks)
        self.assertEqual(gm.running_tasks[mock_file], mock_process)


if __name__ == '__main__':
    unittest.main()
