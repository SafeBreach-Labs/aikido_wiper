from abc import ABC, abstractmethod, ABCMeta
from typing import Iterable


class IDeleteProxy(ABC):
    """
    A proxy for deleting a file or a directory on the computer without doing it directly.
    """
    
    @abstractmethod
    def indirect_delete_paths(self, paths_to_delete: list[str]) -> set[str]:
        """
        Using the proxy, trying to delete a list of given paths.

        :param paths_to_delete: The list of paths to try to delete
        :return: A set of paths that the proxy has failed to delete.
        """
        raise NotImplementedError()

