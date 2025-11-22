"""Service for managing job lifecycle and operations"""

from math import ceil, floor
import os

from utils.file_utils import assert_file_exists, get_file_size
from utils.errors import NotFoundError, ConflictError
from utils.config import config
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


def _awesome_calulations(file1_size, file2_size) -> dict[str, int]:
    cpu_cores = int(os.cpu_count())
    available_cpu_cores = cpu_cores - config.CPU_CORES_RESERVE

    available_ram = (
        os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
    ) / 1024**2  # in MB
    usable_ram = (
        available_ram * config.MEMORY_USAGE_FACTOR * config.MEMORY_SAFETY_BUFFER
    )

    larger_file_size = max(file1_size, file2_size) / (1024**2)  # in MB

    # recon workers
    recon_workers = available_cpu_cores

    # initial bucket count
    initial_buckets_count = recon_workers * config.WOKER_MULTIPLIER

    # memory constraint bucket size
    memory_per_worker = usable_ram / recon_workers
    max_bucket_size = memory_per_worker / 2
    max_bucket_size = min(max_bucket_size, config.MAX_BUCKET_SIZE)

    # file size constraint bucket count
    min_buckets_for_files = ceil(larger_file_size / max_bucket_size)
    bucket_count = max(initial_buckets_count, min_buckets_for_files)

    # apply bucket size floor
    actual_bucket_size = larger_file_size / bucket_count

    if actual_bucket_size < config.MIN_BUCKET_SIZE:
        bucket_count = floor(larger_file_size / config.MIN_BUCKET_SIZE)

        bucket_count = max(bucket_count, config.MIN_BUCKETS)

        actual_bucket_size = larger_file_size / bucket_count

    # apply hard bounds
    def clamp(value, lower_limit, upper_limit):
        return max(lower_limit, min(value, upper_limit))

    bucket_count = clamp(bucket_count, config.MIN_BUCKETS, config.MAX_BUCKETS)
    actual_bucket_size = larger_file_size / bucket_count

    # determine read workers
    num_chunks = ceil(larger_file_size / (config.CHUNK_SIZE))
    read_workers = min(available_cpu_cores, num_chunks)

    return {
        "bucket_count": int(bucket_count),
        "bucket_size": int(actual_bucket_size),
        "recon_workers": int(recon_workers),
        "read_workers": int(read_workers),
    }


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

    calculations = _awesome_calulations(size1, size2)
    bucket_count = calculations["bucket_count"]
    bucket_size = calculations["bucket_size"]
    recon_workers = calculations["recon_workers"]
    read_workers = calculations["read_workers"]

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
        bucket_count=bucket_count,
        bucket_size=bucket_size,
        recon_workers=recon_workers,
        read_workers=read_workers,
        hash_algorithm="default",
    )

    # persist plan back
    job["execution_plan"] = plan.model_dump()
    job["status"] = JobStatus.PREPARED

    add_job_in_store(job_id, job)

    return plan
