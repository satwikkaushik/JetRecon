"""Service for estimating file chunking based on file size and chunk size"""

import math
from utils.file_utils import get_file_size

DEFAULT_CHUNK_SIZE_MB = 2


def estimate_chunks(
    file_size_bytes: int, chunk_size_mb: int = DEFAULT_CHUNK_SIZE_MB
) -> int:
    """Estimate the number of chunks for a given file size and chunk size"""

    chunk_size_bytes = chunk_size_mb * 1024 * 1024
    return max(1, math.ceil(file_size_bytes / chunk_size_bytes))


def find_row_safe_boundary(file_path: str, est_chunks: int):
    """
    Splits file into row-safe chunks
    Ensures:
        - no row is cut in half
        - chunks fully cover file with no gaps
        - each chunk begins at row boundary
        - each chunk ends at row boundary (except final chunk)
    """

    size = get_file_size(file_path)

    # trivial case
    if est_chunks <= 1 or size == 0:
        return [(0, size)]

    raw_chunk_bytes = size // est_chunks
    boundaries = []
    start = 0

    with open(file_path, "rb") as f:
        for i in range(est_chunks):

            # last chunk -> goes to end of file
            if i == est_chunks - 1:
                boundaries.append((start, size))
                break

            tentative_end = start + raw_chunk_bytes
            if tentative_end >= size:
                tentative_end = size

            f.seek(tentative_end)

            # move forward until newline
            while True:
                b = f.read(1)

                if not b:
                    # EOF
                    tentative_end = size
                    break

                if b == b"\n":
                    tentative_end = f.tell()
                    break

            # guarantee monotonic and safe split
            if tentative_end <= start:
                tentative_end = start  # no progress, prevent infinite boundary

            boundaries.append((start, tentative_end))
            start = tentative_end  # next chunk begins here

    return boundaries


def find_number_of_buckets():
    """Placeholder for future bucket calculation logic"""
    return None
