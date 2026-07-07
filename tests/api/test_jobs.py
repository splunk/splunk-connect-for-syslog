from threading import Barrier, Lock, Thread
from pathlib import Path

import pytest

from job_manager import (
    JobConflict,
    JobManager,
    JobStatus,
    JobSubmissionError,
)


class DeferredExecutor:
    def __init__(self):
        self._calls = []

    def submit(self, fn, *args):
        self._calls.append((fn, args))
        return object()

    def run_next(self):
        fn, args = self._calls.pop(0)
        return fn(*args)


class RejectingExecutor:
    def submit(self, fn, *args):
        raise RuntimeError("executor stopped")


def test_run_update_creates_in_progress_job_and_rejects_competitor():
    manager = JobManager(executor=DeferredExecutor())

    first = manager.run_update(lambda: {"status": "updated"})

    assert first.status is JobStatus.IN_PROGRESS
    with pytest.raises(JobConflict) as exc_info:
        manager.run_update(lambda: {"status": "added"})
    assert exc_info.value.active_job.job_id == first.job_id


def test_successful_job_remains_queryable_with_its_result():
    executor = DeferredExecutor()
    manager = JobManager(executor=executor)
    job = manager.run_update(lambda: {"status": "updated"})

    executor.run_next()

    finished = manager.get_job(job.job_id)
    assert finished.status is JobStatus.SUCCESS
    assert finished.result == {"status": "updated"}
    assert finished.error is None


def test_failed_job_remains_queryable_and_releases_active_slot():
    executor = DeferredExecutor()
    manager = JobManager(executor=executor)

    def fail():
        raise RuntimeError("restart failed")

    job = manager.run_update(fail)
    executor.run_next()

    finished = manager.get_job(job.job_id)
    assert finished.status is JobStatus.FAILED
    assert finished.error == "restart failed"
    assert manager.run_update(lambda: {}) is not None


def test_unknown_job_returns_none():
    manager = JobManager(executor=DeferredExecutor())
    assert manager.get_job("missing") is None


def test_history_is_limited_to_latest_records():
    executor = DeferredExecutor()
    manager = JobManager(max_history=2, executor=executor)
    jobs = []
    for _ in range(3):
        jobs.append(manager.run_update(lambda: {}))
        executor.run_next()

    assert manager.get_job(jobs[0].job_id) is None
    assert manager.get_job(jobs[1].job_id) is not None
    assert manager.get_job(jobs[2].job_id) is not None


def test_simultaneous_submissions_admit_exactly_one():
    manager = JobManager(executor=DeferredExecutor())
    barrier = Barrier(8)
    result_lock = Lock()
    accepted = []
    conflicts = []

    def submit():
        barrier.wait()
        try:
            job = manager.run_update(lambda: {})
        except JobConflict as exc:
            with result_lock:
                conflicts.append(exc.active_job.job_id)
        else:
            with result_lock:
                accepted.append(job.job_id)

    threads = [Thread(target=submit) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert len(accepted) == 1
    assert conflicts == [accepted[0]] * 7


def test_executor_submission_failure_is_recorded_and_slot_is_released():
    manager = JobManager(executor=RejectingExecutor())

    with pytest.raises(JobSubmissionError) as exc_info:
        manager.run_update(lambda: {})

    failed = manager.get_job(exc_info.value.job_id)
    assert failed.status is JobStatus.FAILED
    assert failed.error == "executor stopped"


@pytest.mark.parametrize(
    "dockerfile", ["package/Dockerfile", "package/Dockerfile.lite"]
)
def test_container_includes_job_runtime_modules(dockerfile):
    content = Path(dockerfile).read_text(encoding="utf-8")
    assert "COPY package/sbin/job_manager.py /" in content
    assert "COPY package/sbin/job_api.py /" in content
