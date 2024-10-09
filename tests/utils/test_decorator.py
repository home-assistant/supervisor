"""Helper for decorators."""

from supervisor.jobs.decorator import Job


def get_job_decorator(func):
    """Get Job object of decorated function."""
    # Access the closure of the wrapper function
    closure = func.__closure__
    if closure:
        for cell in closure:
            obj = cell.cell_contents
            if isinstance(obj, Job):
                return obj
    return None
