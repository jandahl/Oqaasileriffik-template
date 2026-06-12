#!/usr/bin/env python3
import json
import logging
import os
import secrets
from datetime import datetime, timezone
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import jsonschema

# Configure basic logging
log = logging.getLogger(__name__)


def write_atomic(path: Path, data: Any, indent: int | None = 2) -> None:
    """Safely write JSON data to path using an atomic rename."""
    parent = path.parent
    parent.mkdir(parents=True, exist_ok=True)
    tmp_path = parent / f".{path.name}.{secrets.token_hex(8)}.tmp"
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
    except BaseException as e:
        try:
            tmp_path.unlink(missing_ok=True)
        except OSError:
            pass
        if isinstance(e, OSError):
            args = list(e.args)
            if len(args) > 2 and args[2] == str(tmp_path):
                args[2] = str(path)
            if len(args) > 4 and args[4] == str(tmp_path):
                args[4] = str(path)
            if len(args) > 4 and args[2] == args[4]:
                args[4] = None
            raise type(e)(*args) from e
        raise


def validate_output(data: dict[str, Any], schema_path: Path) -> None:
    """Validate data against the JSON Schema."""
    schema = json.loads(schema_path.read_text(encoding='utf-8'))
    jsonschema.validate(instance=data, schema=schema)
    log.info("Schema validation passed")


class Pipeline:
    def __init__(self, extractor_func: Callable[[Path], list[dict[str, Any]]], schema_path: Path, meta: dict[str, Any]):
        self.extractor_func = extractor_func
        self.schema_path = schema_path
        self.meta = meta.copy()

    def _run_impl(self, data_dir: Path) -> None:
        if not data_dir.is_dir():
            raise FileNotFoundError(f"Data directory does not exist or is not a directory: {data_dir}")

        extracted_dir = Path("extracted")
        extracted_dir.mkdir(parents=True, exist_ok=True)

        # Update metadata timestamp automatically
        self.meta["generated_at"] = datetime.now(timezone.utc).isoformat()

        log.info("Starting data extraction...")
        source_map_entries = self.extractor_func(data_dir)
        log.info(f"Extracted {len(source_map_entries)} entries.")

        envelope = {
            "meta": self.meta,
            "entries": source_map_entries
        }

        try:
            validate_output(envelope, self.schema_path)
        except (OSError, json.JSONDecodeError, jsonschema.SchemaError, jsonschema.ValidationError) as e:
            log.error(f"Schema validation or read failed: {e}")
            raise

        source_map_path = extracted_dir / "source_map.json"
        write_atomic(source_map_path, envelope)
        log.info(f"Successfully wrote {source_map_path}")

    def run(self, data_dir: Path = Path("data")) -> None:
        self._run_impl(data_dir)
