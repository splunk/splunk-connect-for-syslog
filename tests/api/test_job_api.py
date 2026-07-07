from flask import Flask

from job_api import init_job_manager, job_bp, submit_job
from job_manager import JobManager
from test_jobs import DeferredExecutor, RejectingExecutor


def create_app(manager: JobManager) -> Flask:
    app = Flask(__name__)
    init_job_manager(app, manager)
    app.register_blueprint(job_bp)

    @app.post("/submit")
    def submit():
        return submit_job(lambda: {"status": "updated"})

    return app


def test_submit_returns_202_with_job_id_and_location():
    app = create_app(JobManager(executor=DeferredExecutor()))

    response = app.test_client().post("/submit")

    assert response.status_code == 202
    assert response.get_json()["status"] == "success"
    job_id = response.get_json()["job_id"]
    assert response.headers["Location"] == f"/jobs/{job_id}"


def test_conflict_identifies_active_job():
    app = create_app(JobManager(executor=DeferredExecutor()))
    client = app.test_client()
    accepted = client.post("/submit")

    conflict = client.post("/submit")

    assert conflict.status_code == 409
    assert conflict.get_json()["active_job"] == {
        "job_id": accepted.get_json()["job_id"],
        "url": accepted.headers["Location"],
    }


def test_get_job_returns_serializable_state_and_result():
    executor = DeferredExecutor()
    app = create_app(JobManager(executor=executor))
    client = app.test_client()
    accepted = client.post("/submit")
    job_id = accepted.get_json()["job_id"]

    assert client.get(f"/jobs/{job_id}").get_json() == {
        "job_id": job_id,
        "status": "in_progress",
    }

    executor.run_next()
    assert client.get(f"/jobs/{job_id}").get_json() == {
        "job_id": job_id,
        "status": "success",
        "result": {"status": "updated"},
    }


def test_get_unknown_job_returns_404():
    app = create_app(JobManager(executor=DeferredExecutor()))

    response = app.test_client().get("/jobs/missing")

    assert response.status_code == 404
    assert response.get_json()["message"] == "Job not found"


def test_executor_submission_failure_returns_500():
    app = create_app(JobManager(executor=RejectingExecutor()))

    response = app.test_client().post("/submit")

    assert response.status_code == 500
    body = response.get_json()
    assert body["message"] == "Job submission failed"
    assert body["job_id"]
    assert body["url"] == f"/jobs/{body['job_id']}"
