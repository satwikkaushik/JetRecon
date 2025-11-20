"""Service for managing job lifecycle and operations"""

from utils.file_utils import assert_file_exists, get_file_size
from utils.errors import NotFoundError, ConflictError
from services.chunking import (
    estimate_chunks,
    find_row_safe_boundary,
    find_number_of_buckets,
)
from services.job_store import generate_job_id, add_job_in_store, get_job_from_store
from schemas.jobs import JobResponse, JobStatus
from schemas.execution_plan import ExecutionPlan, FilePlan, ChunkInfo
from utils.errors import ProcessingError


def create_job(file1: str, file2: str) -> str:
    """Create a new job for processing a file in chunks"""

    try:
        assert_file_exists(file1)
        assert_file_exists(file2)

        size1 = get_file_size(file1)
        size2 = get_file_size(file2)

        # Estimate chunk counts
        chunks1 = estimate_chunks(size1)
        chunks2 = estimate_chunks(size2)

        job_id = generate_job_id()

        job_data = JobResponse(
            job_id=job_id,
            file1=file1,
            file2=file2,
            chunks_file1=chunks1,
            chunks_file2=chunks2,
            size_file1=size1,
            size_file2=size2,
            status=JobStatus.CREATED,
        )

        add_job_in_store(job_id, job_data)
    except Exception as e:
        raise ProcessingError(message="Failed to create job", details={"error": str(e)})

    return job_id


def prepare_job(job_id: str) -> ExecutionPlan:
    """Prepare the job by creating an execution plan with row-safe chunk boundaries"""

    job_model = get_job_from_store(job_id)
    if not job_model:
        raise NotFoundError(message=f"Job with ID {job_id} not found")

    # normalize model → dict
    job = (
        job_model.model_dump() if hasattr(job_model, "model_dump") else dict(job_model)
    )

    if job.get("execution_plan"):
        raise ConflictError(message=f"Job with ID {job_id} is already prepared")

    size1 = job["size_file1"]
    size2 = job["size_file2"]
    chunks1 = job["chunks_file1"]
    chunks2 = job["chunks_file2"]
    file1_path = job["file1"]
    file2_path = job["file2"]

    boundaries1 = find_row_safe_boundary(file1_path, chunks1)
    boundaries2 = find_row_safe_boundary(file2_path, chunks2)

    plan = ExecutionPlan(
        job_id=job_id,
        file1=FilePlan(
            path=file1_path,
            size=size1,
            chunks=[
                ChunkInfo(chunk_id=i, start=s, end=e)
                for i, (s, e) in enumerate(boundaries1)
            ],
        ),
        file2=FilePlan(
            path=file2_path,
            size=size2,
            chunks=[
                ChunkInfo(chunk_id=i, start=s, end=e)
                for i, (s, e) in enumerate(boundaries2)
            ],
        ),
        bucket_count=find_number_of_buckets() or 16,  # << GOOD DEFAULT
        hash_algorithm="default",
    )

    # persist plan back
    job["execution_plan"] = plan.model_dump()
    job["status"] = JobStatus.PREPARED

    add_job_in_store(job_id, job)

    return plan
