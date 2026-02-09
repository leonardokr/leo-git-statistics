import os

class FileSystem:
    """
    Utility class for common file system operations.
    """

    @staticmethod
    def ensure_directory(path: str) -> None:
        """
        Creates a directory if it does not already exist.

        :param path: The directory path to ensure.
        """
        if not os.path.isdir(path):
            os.makedirs(path, exist_ok=True)

    @staticmethod
    def read_file(path: str) -> str:
        """
        Reads the content of a file as a string.

        :param path: The path to the file.
        :return: File content as a string.
        """
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    @staticmethod
    def write_file(path: str, content: str) -> None:
        """
        Writes string content to a file.

        :param path: The path to the file.
        :param content: The string content to write.
        """
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
