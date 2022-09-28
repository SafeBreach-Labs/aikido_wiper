import argparse

from .consts import *
from aikido_wiper.indirect_ops.delete.idelete_proxy import IDeleteProxy
from .args_specific_actions import get_preferred_proxy_arg_name


def create_proxy_from_conf(args) -> IDeleteProxy:
    """
    Creates the deletion proxy given in the configuration. If a proxy was not picked
    then automatically chooses the best deletion proxy to create.

    :param args: The args parsed by argparse.
    :return: The created deletion proxy.
    """
    if None == args.proxy:
        args.proxy = get_preferred_proxy_arg_name()

    create_func = PROXY_ARG_NAME_TO_PROXY_CREATOR[args.proxy][0]
    proxy_class = PROXY_ARG_NAME_TO_PROXY_CREATOR[args.proxy][1]
    return create_func(proxy_class, args)


def find_deletion_targets_from_args(args) -> set[str]:
    """
    Finds the deletion targets based on the command line arguments.

    :param args: The args parsed by argparse.
    :return: A set of the paths to delete.
    """
    target_const_value = DeletionTargetsOptions[args.deletion_target]
    return DELETION_TARGETS_FINDERS[target_const_value](args)


def erase_traces_based_on_args(args):
    """
    Erases traces of file leftovers in the disk based on the erase traces point
    that was given in the configuration. If it was not given in the configuration then
    the default one for each proxy is picked.

    :param args: The args parsed by argparse.
    """
    if None == args.erase_traces_point:
        target_const_value = PROXY_ARG_NAME_TO_DEFAULT_ERASE_TRACES_POINT[args.proxy]
    else:
        target_const_value = EraseTracesPoint[args.erase_traces_point]
    ERASE_TRACES_POINTS_ACTIONS[target_const_value]()


def parse_args():
    parser = argparse.ArgumentParser(description="Aikido Wiper - Next gen wiping")
    parser.add_argument("-q","--quiet", help="If specified, the wiper will run in the background", action="store_true")

    mode_subparsers = parser.add_subparsers(title="mode", dest="mode", required=True)
    proxy_delete_parser = mode_subparsers.add_parser("PROXY_DELETION")
    erase_disk_traces_parser = mode_subparsers.add_parser("ERASE_DISK_TRACES")

    proxy_delete_parser.add_argument("-p","--proxy", help="The proxy security control to use", type=str, choices=PROXY_ARG_NAME_TO_PROXY_CREATOR.keys())

    erace_traces_points_option_strings = [option.name for option in DeletionTargetsOptions]
    proxy_delete_parser.add_argument("-etp","--erase-traces-point", help="When to execute the part of the wiping that fills the disk to remove traces of deleted files", type=str, choices=erace_traces_points_option_strings)
    
    delete_target_subparsers = proxy_delete_parser.add_subparsers(title="deletion_target", dest="deletion_target", required=True)

    all_dirs_parser = delete_target_subparsers.add_parser(DeletionTargetsOptions.ALL_USER_DATA.name, help="Try to delete the home directory of a certain user")
    all_dirs_parser.add_argument("target_user", help="The target user to delete its home directory", type=str)

    all_files_parser = delete_target_subparsers.add_parser(DeletionTargetsOptions.ALL_FILES_UNDER_PATH.name, help="Try to delete all the files under the Windows drive")
    all_files_parser.add_argument("root_path", help="The parent path for all the file to delete", type=str)
    all_files_parser.add_argument("--exclusion-list-path", help="Path to a file with a list of paths to exclude and not mark", required=False)

    custom_paths_parser = delete_target_subparsers.add_parser(DeletionTargetsOptions.CUSTOM_PATHS.name, help="Try to delete custom paths")
    custom_paths_parser.add_argument("custom_paths_file", help="Path to a file with a list of paths to try to delete", type=str)

    proxy_delete_parser.add_argument("--decoy-root-dir", help="The path in which all the decoys will be placed in case of a usage of a JunctionSwitchProxy", required=False)

    return parser.parse_args()




