"""Service for estimating file chunking based on file size and chunk size"""

import math

DEFAULT_CHUNK_SIZE_MB = 2


def estimate_chunks(
    file_size_bytes: int, chunk_size_mb: int = DEFAULT_CHUNK_SIZE_MB
) -> int:
    """Estimate the number of chunks for a given file size and chunk size"""

    chunk_size_bytes = chunk_size_mb * 1024 * 1024
    return max(1, math.ceil(file_size_bytes / chunk_size_bytes))
