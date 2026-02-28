from filelock import FileLock


class FileLocker:
    """Context manager that holds an exclusive file lock for the duration of a block.

    Usage::

        with FileLocker("myfile.csv"):
            # exclusive access guaranteed here
            process(file)
    """

    def __init__(self, filepath: str):
        self.filepath = filepath
        self._lock = FileLock(f"{filepath}.lock")

    def __enter__(self) -> "FileLocker":
        self._lock.acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self._lock.release()
