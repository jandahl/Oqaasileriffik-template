#!/usr/bin/env python3
import copy
import json
import logging
import os
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import jsonschema  # type: ignore

# Configure basic logging
log = logging.getLogger(__name__)


def write_atomic(path: Path | str, data: Any, indent: int | None = 2) -> None:
    """Safely write JSON data to path using an atomic rename."""
    path = Path(path)
    parent = path.parent
    parent.mkdir(parents=True, exist_ok=True)
    tmp_path = parent / f".{path.name}.{secrets.token_hex(8)}.tmp"
    written = False
    try:
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
            f.write("\n")
            f.flush()
            try:
                os.fsync(f.fileno())
            except OSError:
                pass
        os.replace(tmp_path, path)
        written = True
        try:
            dir_fd = os.open(parent, os.O_RDONLY)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
        except OSError:
            pass
    finally:
        if not written:
            try:
                tmp_path.unlink(missing_ok=True)
            except OSError:
                pass


def validate_output(data: dict[str, Any], schema: dict[str, Any]) -> None:
    """Validate data against the JSON Schema."""
    jsonschema.validate(instance=data, schema=schema)
    log.info("Schema validation passed")


class Pipeline:
    def __init__(
        self,
        extractor_func: Callable[[Path], list[dict[str, Any]]],
        schema_path: Path | str,
        meta: dict[str, Any],
        output_dir: Path | str = Path("extracted")
    ):
        if not callable(extractor_func):
            raise TypeError("extractor_func must be a callable")
        if not isinstance(meta, dict):
            raise TypeError("meta must be a dictionary")

        self.extractor_func = extractor_func
        self.schema_path = Path(schema_path)
        self.meta = copy.deepcopy(meta)
        self.output_dir = Path(output_dir)

        # Load and parse schema early to fail fast if it is missing or invalid
        try:
            self.schema = json.loads(self.schema_path.read_text(encoding='utf-8'))
            jsonschema.validators.validator_for(self.schema).check_schema(self.schema)
        except Exception as e:
            raise ValueError(f"Failed to load schema from {schema_path}: {e}") from e

    def _run_impl(self, data_dir: Path) -> None:
        if not data_dir.is_dir():
            raise FileNotFoundError(f"Data directory does not exist or is not a directory: {data_dir}")

        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Update metadata timestamp automatically
        run_meta = copy.deepcopy(self.meta)
        run_meta["generated_at"] = datetime.now(timezone.utc).isoformat()

        log.info("Starting data extraction...")
        source_map_entries = self.extractor_func(data_dir)
        if not isinstance(source_map_entries, list):
            raise TypeError(f"The extractor function must return a list of entries, got {type(source_map_entries).__name__}")
        log.info(f"Extracted {len(source_map_entries)} entries.")

        envelope = {
            "meta": run_meta,
            "entries": source_map_entries
        }

        try:
            validate_output(envelope, self.schema)
        except (jsonschema.SchemaError, jsonschema.ValidationError) as e:
            log.error(f"Schema validation failed: {e}")
            raise

        source_map_path = self.output_dir / "source_map.json"
        write_atomic(source_map_path, envelope)
        log.info(f"Successfully wrote {source_map_path}")

    def run(self, data_dir: Path | str = Path("data")) -> None:
        self._run_impl(Path(data_dir))
