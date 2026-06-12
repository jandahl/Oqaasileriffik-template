#!/usr/bin/env python3
import argparse
import json
import logging
import os
import secrets
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

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
            if e.filename == str(tmp_path):
                e.filename = str(path)
                if e.filename2 == str(path):
                    e.filename2 = None
            elif e.filename2 == str(tmp_path):
                e.filename2 = str(path)
        raise


def validate_output(data: dict[str, Any], schema_path: Path) -> None:
    """Validate data against the JSON Schema."""
    schema = json.loads(schema_path.read_text(encoding='utf-8'))
    jsonschema.validate(instance=data, schema=schema)
    log.info("Schema validation passed")


def extract_data(input_dir: Path) -> list[dict[str, Any]]:
    """
    TODO: Implement parsing logic for the specific upstream data source.
    Return a list of raw entries in the format:
    [
        {
            "source_id": "...",
            "raw_data": {
                "lexeme": "...",
                "word_class": "...",
                "gloss_en": "..."
            }
        }
    ]
    """
    entries = []
    # e.g. parse files in input_dir...
    return entries


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        _main_impl()
    except FileNotFoundError as e:
        log.error("File not found: %s", e)
        sys.exit(1)
    except OSError:
        log.exception("File operation failed")
        sys.exit(1)


def _main_impl() -> None:
    parser = argparse.ArgumentParser(description="Oqaasileriffik Data Conversion Pipeline Template")
    parser.add_argument("--data-dir", type=Path, default=Path("data"), help="Path to input data directory")
    args = parser.parse_args()

    if not args.data_dir.is_dir():
        log.error(f"Data directory does not exist or is not a directory: {args.data_dir}")
        sys.exit(1)

    # Paths
    script_dir = Path(__file__).resolve().parent
    schema_path = script_dir / "schema.json"
    extracted_dir = Path("extracted")

    # Create output directory
    extracted_dir.mkdir(parents=True, exist_ok=True)

    # Metadata Envelope
    meta = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "license": "MPL-2.0 (Mozilla Public License 2.0) + Rights Reserved",
        "attribution": "TODO: Author / Source",
        "source_repo": "TODO: URL to the upstream data repository",
        "available_fields": ["lexeme", "word_class", "gloss_en"],
    }

    log.info("Starting data extraction...")
    source_map_entries = extract_data(args.data_dir)

    log.info(f"Extracted {len(source_map_entries)} entries.")

    envelope = {
        "meta": meta,
        "entries": source_map_entries
    }

    try:
        validate_output(envelope, schema_path)
    except OSError as e:
        log.error(f"Failed to read schema file at {schema_path}: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        log.error(f"Schema file at {schema_path} is not valid JSON: {e}")
        sys.exit(1)
    except jsonschema.SchemaError as e:
        log.error(f"Schema file at {schema_path} is itself invalid: {e.message}")
        sys.exit(1)
    except jsonschema.ValidationError as e:
        log.error(f"Schema validation failed: {e.message}")
        sys.exit(1)

    # Write source_map.json
    source_map_path = extracted_dir / "source_map.json"
    write_atomic(source_map_path, envelope)
    log.info(f"Successfully wrote {source_map_path}")


if __name__ == "__main__":
    main()
