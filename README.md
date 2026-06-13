# Oqaasileriffik Pipeline Core Library

This repository contains the `oqaasileriffik_pipeline` Python library, providing the core environment, logging, atomic file handling, and validation pipeline for Oqaasileriffik data extraction projects.

It enforces a standardized, bulletproof environment including:
* Strict `OSError` handling and atomic file writes.
* Exception metadata preservation.
* Linting and formatting with `ruff`.
* Type checking with `mypy`.
* Standardized `UPSTREAM_MAP_DESIGN` envelope generation.

> [!WARNING]
> **Windows environments are strictly unsupported.** This library and its bootstrap scripts rely on Unix primitives (`os.fsync`, atomic POSIX renames) that may degrade or behave unpredictably on Windows. Any use on Windows, msys, cygwin, or mingw will fail immediately by design.

## Getting Started

1. Downstream repositories (e.g., `dicts`, `katersat`) should NOT clone this repository directly. Instead, include it in your `pyproject.toml` dependencies:
   ```toml
   dependencies = [
       "oqaasileriffik-template @ git+https://github.com/jandahl/Oqaasileriffik-template.git"
   ]
   ```

2. Create your extraction script and call the `Pipeline` class:
   ```python
   from pathlib import Path
   from typing import Any
   from oqaasileriffik_pipeline import Pipeline

   def my_extractor(data_dir: Path) -> list[dict[str, Any]]:
       # Your custom data extraction logic here
       return [{"lexeme": "...", "word_class": "..."}]

   if __name__ == "__main__":
       meta = {
           "schema_version": "1.0",
           "license": "MPL-2.0 (Mozilla Public License 2.0) + Rights Reserved",
           "attribution": "Upstream Author",
           "source_repo": "https://github.com/...",
           "available_fields": ["lexeme", "word_class"]
       }
       schema_path = Path(__file__).parent / "schema.json"

       pipeline = Pipeline(
           extractor_func=my_extractor, 
           schema_path=schema_path, 
           meta=meta
       )
       pipeline.run()
   ```

## License
Default license: Mozilla Public License 2.0 (MPL-2.0) + Rights Reserved.
