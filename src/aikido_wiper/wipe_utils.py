import shutil
import pathlib
import progressbar
import tempfile
import os
import uuid
import random
from typing import Callable

def erase_disk_traces(iterations = 10):
    """
    Erases disk traces of any files which were deleted. Fills the free space in the disk with
    random bytes and then deletes them a number of times.

    :param iterations: Optional, the number of times to fill the free space on disk, defaults to 10.
    """
    for i in range(iterations):
        temp_file_path = fill_disk_free_space()
        os.remove(temp_file_path)

def fill_disk_free_space(chunk_size = 1024 * 1024) -> str:
    """
    Fills the free space on the disk with random bytes. It does it by creating one huge file.

    :param chunk_size: Optional, the amount of random bytes to add to the file each time, defaults
        to 1024*1024
    :return: The path of the file that was used in order to fill the disk.
    """
    windows_drive = pathlib.Path.home().drive + "\\"
    free_space = shutil.disk_usage(windows_drive)[2]
    temp_file_path = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
    with open(temp_file_path, "ab+") as target_file:
        with progressbar.ProgressBar(max_value=free_space) as bar:
            bar_space_filled = 0
            while 0 < free_space:
                if free_space < chunk_size:
                    chunk_size = free_space
                target_file.write(random.randbytes(chunk_size))
                free_space -= chunk_size

                # progress bar update
                bar_space_filled += chunk_size
                bar.update(bar_space_filled)

    return temp_file_path

def get_all_matching_elements_under_dir(dir_path: str, does_match_func: Callable[[str], bool], exclude_list=None) -> set[str]:
    """
    Recursively iterates through all directories and files under a certain path. For each directory
    or file, calls a given function to determine if the directory or file matches a condition.

    :param dir_path: The root directory for the search.
    :param does_match_func: The function that determines for each directory or file if it
        matches a condition
    :param exclude_list: Optional, paths to exclude from the result and the search. If a directory
        is excluded then all the directories and files inside it are excluded as well.
    :return: A set of the matching directories and files.
    """
    try:
        sub_elements = os.listdir(dir_path)
    except FileNotFoundError:
        return set()
    except PermissionError:
        return {dir_path}

    matching_elements = set()
    if None == exclude_list:
        exclude_list = set()

    for sub_element_name in sub_elements:
        sub_element_path = os.path.join(dir_path, sub_element_name)
        if sub_element_path not in exclude_list:
            if does_match_func(sub_element_path):
                matching_elements.add(sub_element_path)

            if os.path.isdir(sub_element_path):
                matching_elements = matching_elements.union(get_all_matching_elements_under_dir(sub_element_path, does_match_func, exclude_list))

    return matching_elements

def get_all_dirs_under_dir(dir_path, exclude_list=None) -> set[str]:
    """
    Calls get_all_matching_elements_under_dir() with a condition of being a directory.

    :param dir_path: same as in get_all_matching_elements_under_dir().
    :param exclude_list: same as in get_all_matching_elements_under_dir().
    :return: same as in get_all_matching_elements_under_dir().
    """
    return get_all_matching_elements_under_dir(dir_path, os.path.isdir, exclude_list)

def get_all_files_under_dir(dir_path, exclude_list=None) -> set[str]:
    """
    Calls get_all_matching_elements_under_dir() with a condition of being a file.

    :param dir_path: same as in get_all_matching_elements_under_dir().
    :param exclude_list: same as in get_all_matching_elements_under_dir().
    :return: same as in get_all_matching_elements_under_dir().
    """
    return get_all_matching_elements_under_dir(dir_path, os.path.isfile, exclude_list)
