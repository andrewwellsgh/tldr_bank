from filelock import FileLock

class FileLocker:
    """Context manager for locking files during processing."""

    def __init__(self, filepath):
        self.filepath = filepath
        self.lockfile = f"{filepath}.lock"

    def __enter__(self):
        self.lock = FileLock(self.lockfile)
        self.lock.acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.lock.release()

    def run(self):
        return self
