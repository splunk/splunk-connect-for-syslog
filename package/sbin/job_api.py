from typing import Callable

from flask import Flask, current_app, Blueprint, jsonify, url_for

from job_manager import JobConflict, JobManager, JobSubmissionError

JOB_MANAGER_EXTENSION = "sc4s_job_manager"

job_bp = Blueprint("jobs", __name__)


def init_job_manager(
    app: Flask,
    manager: JobManager | None = None,
) -> JobManager:
    manager = manager or JobManager()
    app.extensions[JOB_MANAGER_EXTENSION] = manager
    return manager


def get_job_manager() -> JobManager:
    return current_app.extensions[JOB_MANAGER_EXTENSION]


def _get_status_url(job_id: str) -> str:
    return url_for("jobs.get_job_status", job_id=job_id)


def submit_job(work: Callable[[], dict]):
    job_manager = get_job_manager()
    try:
        job = job_manager.run_update(work)
    except JobConflict as exc:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Another configuration job is in progress",
                    "active_job": {
                        "job_id": exc.active_job.job_id,
                        "url": _get_status_url(exc.active_job.job_id),
                    },
                }
            ),
            409,
        )
    except JobSubmissionError as exc:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": str(exc),
                    "job_id": exc.job_id,
                    "url": _get_status_url(exc.job_id),
                }
            ),
            500,
        )

    url = _get_status_url(job.job_id)
    response = jsonify({"status": "success", "job_id": job.job_id})
    response.headers["Location"] = url
    response.status_code = 202
    return response


@job_bp.route("/jobs/<job_id>", methods=["GET"])
def get_job_status(job_id: str):
    job_manager = get_job_manager()
    job = job_manager.get_job_dict(job_id)
    if job is None:
        return jsonify({"status": "error", "message": "Job not found"}), 404
    return jsonify(job), 200
