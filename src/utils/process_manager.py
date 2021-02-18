import os
import sys
import psutil

from typing import List


class ProcessManager:
    def __init__(self, process_name: str):
        self.process_name = process_name
        self.pids = []

    def kill(self, pids: List[str] = None):
        if self.pids:
            self.pids = []
        """
        Kills processes from a supplied list of pids or gets a list of all the PIDs of a all the running process whose
        name contains the given string process_name and kill the process
        """
        if pids:
            for pid in pids:
                print(int(pid))
                if psutil.pid_exists(int(pid)):
                    os.system(f"kill -9 {pid}")
                    self.pids.append(pid)

        # based on https://thispointer.com/python-check-if-a-process-is-running-by-name-and-find-its-process-id-pid/
        # Iterate over the all the running process

        for proc in psutil.process_iter():
            try:
                proc_info = proc.as_dict(attrs=['pid', 'name', 'create_time'])
                # Check if process name contains the given name string.
                if self.process_name in proc_info['name']:
                    if psutil.pid_exists(proc_info['pid']):
                        os.system(f"kill -9 {proc_info['pid']}")
                        self.pids.append(proc_info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as pe:
                sys.stderr.write(str(pe))
