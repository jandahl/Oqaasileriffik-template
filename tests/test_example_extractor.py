import logging
from pathlib import Path
from unittest.mock import patch

from example_extractor.example_extractor import main


def test_cli_parsing_and_verbose_flag():
    # Test that --verbose sets the logging level to DEBUG
    original_level = logging.getLogger().level
    try:
        with patch("example_extractor.example_extractor.Pipeline") as mock_pipeline:
            # Before calling main, set root logger to INFO (the default set by basicConfig)
            logging.getLogger().setLevel(logging.INFO)
            assert logging.getLogger().level == logging.INFO

            # Run with --verbose
            exit_code = main(["--verbose", "--data-dir", "dummy"])
            
            assert exit_code == 0
            mock_pipeline.assert_called_once()
            
            # Check that verbose flag actually set the root logger level to DEBUG
            assert logging.getLogger().level == logging.DEBUG
    finally:
        logging.getLogger().setLevel(original_level)


def test_missing_schema_json():
    # If the schema.json is missing, main should catch FileNotFoundError and return 1
    with patch("example_extractor.example_extractor.Path.is_file", return_value=False):
        exit_code = main(["--data-dir", "dummy"])
        assert exit_code == 1


def test_exception_handling():
    # Test that a random Exception is caught and returns 1
    with patch("example_extractor.example_extractor._main_impl", side_effect=RuntimeError("Some random error")):
        exit_code = main(["--data-dir", "dummy"])
        assert exit_code == 1
