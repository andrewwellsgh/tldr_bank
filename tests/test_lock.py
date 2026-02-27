import os
import pytest

from src.tldr_bank.lock import FileLocker


@pytest.fixture
def lockable_file(tmp_path):
    f = tmp_path / "test.csv"
    f.write_text("data")
    return str(f)


def test_context_manager_acquires(lockable_file):
    with FileLocker(lockable_file) as locker:
        assert locker._lock.is_locked


def test_lock_file_created(lockable_file):
    with FileLocker(lockable_file):
        assert os.path.exists(f"{lockable_file}.lock")


def test_lock_released_after_block(lockable_file):
    with FileLocker(lockable_file) as locker:
        pass
    assert not locker._lock.is_locked


def test_lock_released_on_exception(lockable_file):
    locker = None
    with pytest.raises(ValueError):
        with FileLocker(lockable_file) as locker:
            raise ValueError("simulated error")
    assert not locker._lock.is_locked


def test_returns_self_from_enter(lockable_file):
    with FileLocker(lockable_file) as locker:
        assert isinstance(locker, FileLocker)
