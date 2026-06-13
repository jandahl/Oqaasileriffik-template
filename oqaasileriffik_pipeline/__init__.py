import sys

if sys.platform in ("win32", "cygwin", "msys"):
    raise RuntimeError("Windows and POSIX-on-Windows environments are strictly unsupported by oqaasileriffik_pipeline.")

from oqaasileriffik_pipeline.core import Pipeline, write_atomic

__all__ = ["Pipeline", "write_atomic"]
