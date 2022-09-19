from enum import Enum

from aikido_wiper.indirect_ops.delete.microsoft_defender_delete_proxy import MicrosoftDefenderDeleteProxy
from aikido_wiper.indirect_ops.delete.sentinel_one_delete_proxy import SentinelOneDeleteProxy
from aikido_wiper.wipe_utils import erase_disk_traces
from .args_specific_actions import create_junction_switch_proxy, find_custom_paths_from_args, find_dirs_under_dir_from_args, \
    find_files_under_dir_from_args, autostart_reboot_erase_point, task_scheduler_reboot_erase_point

class EraseTracesPoint(Enum):
    """
    Points in time to initiate the erase traces functionality of the wiper.
    """
    RIGHT_AFTER = 0,
    TASK_SCHEDULER_REBOOT = 1,
    AUTOSTART_REBOOT = 2

class DeletionTargetsOptions(Enum):
    """
    Methods to specify the deletion targets in the command line arguments.
    """
    ALL_DIRS_UNDER_PATH = 0,
    ALL_FILES_UNDER_PATH = 1,
    CUSTOM_PATHS = 2

# Maps the proxy command line argument options to their creators.
# A "creator" creates the proxy based on the args.
PROXY_ARG_NAME_TO_PROXY_CREATOR = {
    MicrosoftDefenderDeleteProxy.__name__: (create_junction_switch_proxy, MicrosoftDefenderDeleteProxy),
    SentinelOneDeleteProxy.__name__: (create_junction_switch_proxy, SentinelOneDeleteProxy)
}

# Maps the deletion targets options to the functions that fetch the final
# set of deletion targets.
DELETION_TARGETS_FINDERS = {
    DeletionTargetsOptions.ALL_DIRS_UNDER_PATH: find_dirs_under_dir_from_args,
    DeletionTargetsOptions.ALL_FILES_UNDER_PATH: find_files_under_dir_from_args,
    DeletionTargetsOptions.CUSTOM_PATHS: find_custom_paths_from_args
}

# Maps erase traces points to the relevant action to do in order to erase
# traces at that point.
ERASE_TRACES_POINTS_ACTIONS = {
    EraseTracesPoint.RIGHT_AFTER: erase_disk_traces,
    EraseTracesPoint.TASK_SCHEDULER_REBOOT: task_scheduler_reboot_erase_point,
    EraseTracesPoint.AUTOSTART_REBOOT: autostart_reboot_erase_point
}

# Maps proxies to their default erase traces point
PROXY_ARG_NAME_TO_DEFAULT_ERASE_TRACES_POINT = {
    MicrosoftDefenderDeleteProxy.__name__:  EraseTracesPoint.TASK_SCHEDULER_REBOOT,
    SentinelOneDeleteProxy.__name__:  EraseTracesPoint.TASK_SCHEDULER_REBOOT
}
