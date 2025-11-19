"""Router for job-related endpoints"""

from fastapi import APIRouter
from schemas.jobs import JobResponse, JobRequest
from services.job_servies import create_job
from services.job_store import (
    get_job_from_store,
    get_all_jobs_from_store,
    delete_job_from_store,
)
from typing import List

router = APIRouter()


@router.get("/", response_model=List[JobResponse])
def list_all_jobs():
    """Endpoint to list all jobs"""
    jobs = get_all_jobs_from_store()
    return list(jobs.values())


@router.post("/", response_model=JobResponse)
def create_new_job(payload: JobRequest):
    """Endpoint to create a new job"""

    job_id: str = create_job(
        file1=payload.file1,
        file2=payload.file2,
    )

    job_data: JobResponse = get_job_from_store(job_id)

    return job_data


@router.get("/{job_id}", response_model=JobResponse)
def get_job_details(job_id: str):
    """Endpoint to get details of a specific job"""

    job_data: JobResponse = get_job_from_store(job_id)

    return job_data


@router.delete("/{job_id}", response_model=dict)
def delete_job(job_id: str):
    """Endpoint to delete a specific job"""

    delete_job_from_store(job_id)
    return {"message": f"Job {job_id} deleted successfully."}
