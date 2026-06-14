#!/usr/bin/env python3
import argparse
import logging
import sys
from pathlib import Path
from typing import Any

from oqaasileriffik_pipeline import Pipeline

# Configure basic logging
log = logging.getLogger(__name__)

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
    entries: list[dict[str, Any]] = []
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
        "license": "MPL-2.0 (Mozilla Public License 2.0) + Rights Reserved",
        "attribution": "TODO: Author / Source",
        "source_repo": "TODO: URL to the upstream data repository",
        "available_fields": ["lexeme", "word_class", "gloss_en"],
    }

    pipeline = Pipeline(
        extractor_func=extract_data,
        schema_path=schema_path,
        meta=meta,
        output_dir=extracted_dir
    )
    
    pipeline.run(args.data_dir)


if __name__ == "__main__":
    main()
