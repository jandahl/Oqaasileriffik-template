#!/usr/bin/env python3
import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import jsonschema

# Configure basic logging
log = logging.getLogger(__name__)


def write_atomic(path: Path, data: Any, indent: int | None = 2) -> None:
    """Safely write JSON data to path using an atomic rename."""
    tmp = path.with_suffix('.tmp')
    try:
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=indent), encoding='utf-8')
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink()


def validate_output(data: dict, schema_path: Path) -> None:
    """Validate data against the JSON Schema."""
    schema = json.loads(schema_path.read_text(encoding='utf-8'))
    jsonschema.validate(instance=data, schema=schema)
    log.info("Schema validation passed")


def extract_data(input_dir: Path) -> list[dict]:
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
    parser = argparse.ArgumentParser(description="Oqaasileriffik Data Conversion Pipeline Template")
    parser.add_argument("--data-dir", type=Path, default=Path("data"), help="Path to input data directory")
    args = parser.parse_args()

    if not args.data_dir.is_dir():
        log.error(f"Data directory does not exist or is not a directory: {args.data_dir}")
        sys.exit(1)

    # Paths
    root_dir = Path(__file__).parent.parent.resolve()
    schema_path = root_dir / "convert" / "schema.json"
    extracted_dir = root_dir / "extracted"

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
    except jsonschema.ValidationError as e:
        log.error(f"Schema validation failed: {e.message}")
        sys.exit(1)

    # Write source_map.json
    source_map_path = extracted_dir / "source_map.json"
    write_atomic(source_map_path, envelope)
    log.info(f"Successfully wrote {source_map_path}")


if __name__ == "__main__":
    main()
