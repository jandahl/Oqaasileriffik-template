#!/usr/bin/env python3
import argparse
import logging
import sys
from pathlib import Path
from typing import Any
import jsonschema

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
    log.info("Extracting data from %s", input_dir)
    # Placeholder: return an empty list or mock data
    entries: list[dict[str, Any]] = []
    # e.g. parse files in input_dir...
    return entries


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        _main_impl(argv)
        return 0
    except FileNotFoundError as e:
        log.error("File not found: %s", e)
        return 1
    except jsonschema.ValidationError:
        # The pipeline already logs the validation error details
        return 1
    except OSError:
        log.exception("File operation failed")
        return 1
    except Exception:
        log.exception("Execution failed")
        return 1


def _main_impl(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Oqaasileriffik Data Conversion Pipeline Template")
    parser.add_argument("--data-dir", type=Path, default=Path("data"), help="Path to input data directory")
    parser.add_argument("--output-dir", type=Path, default=Path("extracted"), help="Path to output directory")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose/debug logging")
    args = parser.parse_args(argv)

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Paths
    script_dir = Path(__file__).resolve().parent
    schema_path = script_dir / "schema.json"
    if not schema_path.is_file():
        raise FileNotFoundError(f"Schema file not found at {schema_path}")

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
        output_dir=args.output_dir
    )
    
    pipeline.run(args.data_dir)


if __name__ == "__main__":
    sys.exit(main())
