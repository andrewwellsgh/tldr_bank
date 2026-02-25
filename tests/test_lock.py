import os
from src.tldr_bank.lock import FileLocker

def test_lock_file():
    testfile = "tests/temp.txt"
    with open(testfile,'w') as f:
        f.write("test")
    with FileLocker(testfile) as lock:
        assert lock is not None
    os.remove(testfile)
    os.remove(testfile + ".lock")
