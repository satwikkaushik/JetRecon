"""Schemas for job requests and responses."""

from pydantic import BaseModel, Field
from typing import Optional, List
import enum
from schemas.execution_plan import ExecutionPlan


class JobStatus(enum.Enum):
    CREATED = "created_pending_processing"
    PREPARED = "prepared_pending_hashing"
    HASHING = "hashing_in_progress"
    RECON = "reconciliation_in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class JobRequest(BaseModel):
    file1: str = Field(..., description="Path to the first file")
    file2: str = Field(..., description="Path to the second file")


class JobResponse(BaseModel):
    job_id: str
    file1: str
    file2: str
    chunks_file1: int
    chunks_file2: int
    size_file1: int
    size_file2: int
    status: JobStatus
    execution_plan: Optional[ExecutionPlan] = None
