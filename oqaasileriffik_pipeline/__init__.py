import sys

if sys.platform.startswith("win") or sys.platform in ("msys", "cygwin"):
    raise RuntimeError("Windows and Windows-based environments (msys, cygwin, mingw) are strictly unsupported.")

from oqaasileriffik_pipeline.core import Pipeline, write_atomic

__all__ = ["Pipeline", "write_atomic"]
