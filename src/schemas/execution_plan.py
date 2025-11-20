"""Execution plan schema for file processing jobs"""

from pydantic import BaseModel
from typing import List


class ChunkInfo(BaseModel):
    chunk_id: int
    start: int
    end: int


class FilePlan(BaseModel):
    path: str
    size: int
    chunks: List[ChunkInfo]


class ExecutionPlan(BaseModel):
    job_id: str
    file1: FilePlan
    file2: FilePlan
    bucket_count: int
    hash_algorithm: str
