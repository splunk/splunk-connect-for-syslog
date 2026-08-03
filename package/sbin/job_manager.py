from collections import OrderedDict
from concurrent.futures import Executor, ThreadPoolExecutor
from dataclasses import dataclass
from enum import Enum, auto
import logging
from threading import Lock
from typing import Callable
from uuid import uuid4

logger = logging.getLogger(__name__)


class JobStatus(Enum):
    SUCCESS = auto()
    FAILED = auto()
    IN_PROGRESS = auto()


@dataclass
class UpdateJob:
    job_id: str
    status: JobStatus
    result: dict | None = None
    error: str | None = None

    def to_dict(self) -> dict:
        payload = {
            "job_id": self.job_id,
            "status": self.status.name.lower(),
        }
        if self.result is not None:
            payload["result"] = self.result
        if self.error is not None:
            payload["error"] = self.error
        return payload


class JobConflict(Exception):
    def __init__(self, active_job: UpdateJob):
        super().__init__("Another update job is in progress")
        self.active_job = active_job


class JobSubmissionError(Exception):
    def __init__(self, job: UpdateJob):
        super().__init__("Job submission failed")
        self.job_id = job.job_id


class JobManager:
    def __init__(
        self,
        max_history: int = 100,
        executor: Executor | None = None,
    ):
        self._max_history = max_history
        self._jobs: OrderedDict[str, UpdateJob] = OrderedDict()
        self._lock = Lock()
        self._executor = executor or ThreadPoolExecutor(
            max_workers=1,
            thread_name_prefix="sc4s_job_manager",
        )
        self._active_job: UpdateJob | None = None

    def run_update(self, work: Callable[[], dict]) -> UpdateJob:
        with self._lock:
            if self._active_job is not None:
                raise JobConflict(self._active_job)

            job = UpdateJob(job_id=str(uuid4()), status=JobStatus.IN_PROGRESS)
            self._jobs[job.job_id] = job
            self._active_job = job
            self._evict_oldest_job()

        try:
            self._executor.submit(self._run, job, work)
        except Exception as exc:
            self._finish_job(job, JobStatus.FAILED, error=str(exc))
            raise JobSubmissionError(job) from exc

        return job

    def get_job(self, job_id: str) -> UpdateJob | None:
        with self._lock:
            return self._jobs.get(job_id)

    def get_job_dict(self, job_id: str) -> dict | None:
        """Serialize a job while holding the lock to avoid torn reads."""
        with self._lock:
            job = self._jobs.get(job_id)
            return job.to_dict() if job is not None else None

    def _run(self, job: UpdateJob, work: Callable[[], dict]):
        try:
            result = work()
        except Exception as exc:
            logger.exception("Update job %s failed", job.job_id)
            self._finish_job(job, JobStatus.FAILED, error=str(exc))
        else:
            self._finish_job(job, JobStatus.SUCCESS, result=result)

    def _finish_job(
        self,
        job: UpdateJob,
        status: JobStatus,
        result: dict | None = None,
        error: str | None = None,
    ):
        with self._lock:
            job.status = status
            job.result = result
            job.error = error
            if self._active_job is job:
                self._active_job = None

    def _evict_oldest_job(self):
        while len(self._jobs) > self._max_history:
            self._jobs.popitem(last=False)
