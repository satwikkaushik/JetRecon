"""In-memory job store service"""

import uuid
from typing import Dict
from utils.errors import NotFoundError, ProcessingError
from schemas.jobs import JobResponse


JOB_STORE: Dict[str, JobResponse] = {}


def generate_job_id() -> str:
    """Generates a unique job ID"""

    return str(uuid.uuid4())


def add_job_in_store(job_id: str, job_data: JobResponse) -> str:
    """Adds a job to the in-memory job store"""

    try:
        JOB_STORE[job_id] = job_data
        return job_id
    except Exception as e:
        raise ProcessingError("Failed to add job", {"job_id": job_id, "error": str(e)})


def get_job_from_store(job_id: str) -> JobResponse:
    """Retrieves a job from the in-memory job store"""

    if job_id not in JOB_STORE:
        raise NotFoundError("Job not found", {"job_id": job_id})

    return JOB_STORE.get(job_id)


def get_all_jobs_from_store() -> Dict[str, JobResponse]:
    """Retrieves all jobs from the in-memory job store"""

    if not JOB_STORE:
        raise NotFoundError("No jobs found in the store")

    return JOB_STORE


def delete_job_from_store(job_id: str) -> str:
    """Deletes a job from the in-memory job store"""

    if job_id not in JOB_STORE:
        raise NotFoundError("Job not found", {"job_id": job_id})

    del JOB_STORE[job_id]

    return job_id
