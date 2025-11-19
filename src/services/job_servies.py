"""Service for managing job lifecycle and operations"""

from utils.file_utils import assert_file_exists, get_file_size
from services.chunking import estimate_chunks
from services.job_store import generate_job_id, add_job_in_store
from schemas.jobs import JobResponse, JobStatus
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
