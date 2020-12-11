import subprocess
import time

def lowpriority():
    """ Set the priority of the process to below-normal."""

    import sys
    try:
        sys.getwindowsversion()
    except AttributeError:
        isWindows = False
    else:
        isWindows = True

    if isWindows:
        # Based on:
        #   "Recipe 496767: Set Process Priority In Windows" on ActiveState
        #   http://code.activestate.com/recipes/496767/
        import win32api,win32process,win32con

        pid = win32api.GetCurrentProcessId()
        handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
        win32process.SetPriorityClass(handle, win32process.BELOW_NORMAL_PRIORITY_CLASS)
    else:
        import os

        os.nice(1)
lowpriority()

run = True
while(run):
	p = subprocess.Popen('C:\\Users\Administrator\\AppData\Local\\Programs\\Python\\Python38\\expiredStakes\\graphql\\runEndStakesDue.bat', shell=True, stdin=subprocess.PIPE)
	stdout, stderr = p.communicate()
	time.sleep(10800)
	p = subprocess.Popen('C:\\Users\Administrator\\AppData\Local\\Programs\\Python\\Python38\\expiredStakes\\graphql\\runEndStakesNotDue.bat', shell=True, stdin=subprocess.PIPE)
	stdout, stderr = p.communicate()
	time.sleep(20800)

