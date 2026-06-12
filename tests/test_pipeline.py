import json
from pathlib import Path
from typing import Any, Callable

import jsonschema  # type: ignore
import pytest

from oqaasileriffik_pipeline.core import Pipeline


@pytest.fixture
def valid_schema_path(tmp_path: Path) -> Path:
    schema_path = tmp_path / "schema.json"
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {
            "meta": {"type": "object"},
            "entries": {"type": "array"}
        },
        "required": ["meta", "entries"]
    }
    schema_path.write_text(json.dumps(schema), encoding='utf-8')
    return schema_path


@pytest.fixture
def mock_extractor() -> Callable:
    def extractor(path: Path) -> list[dict[str, Any]]:
        return [{"id": 1, "value": "test"}]
    return extractor


def test_pipeline_fail_fast_on_missing_schema(mock_extractor: Callable) -> None:
    with pytest.raises(ValueError, match="Failed to load schema from missing.json"):
        Pipeline(mock_extractor, "missing.json", {})


def test_pipeline_fail_fast_on_invalid_json(tmp_path: Path, mock_extractor: Callable) -> None:
    invalid_schema = tmp_path / "invalid.json"
    invalid_schema.write_text("not a json", encoding='utf-8')
    
    with pytest.raises(ValueError, match="Failed to load schema from"):
        Pipeline(mock_extractor, invalid_schema, {})


def test_pipeline_missing_data_dir(valid_schema_path: Path, mock_extractor: Callable) -> None:
    pipeline = Pipeline(mock_extractor, valid_schema_path, {})
    with pytest.raises(FileNotFoundError, match="Data directory does not exist"):
        pipeline.run("does_not_exist")


def test_pipeline_successful_run(tmp_path: Path, valid_schema_path: Path, mock_extractor: Callable) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    
    out_dir = tmp_path / "extracted"
    
    pipeline = Pipeline(
        extractor_func=mock_extractor,
        schema_path=valid_schema_path,
        meta={"source": "test"},
        output_dir=out_dir
    )
    
    pipeline.run(data_dir)
    
    # Verify the output
    out_file = out_dir / "source_map.json"
    assert out_file.exists()
    
    result = json.loads(out_file.read_text(encoding='utf-8'))
    assert "generated_at" in result["meta"]
    assert result["meta"]["source"] == "test"
    assert len(result["entries"]) == 1
    assert result["entries"][0]["value"] == "test"


def test_pipeline_extractor_returns_none(tmp_path: Path, valid_schema_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    out_dir = tmp_path / "extracted"

    def none_extractor(path: Path) -> Any:
        return None

    pipeline = Pipeline(
        extractor_func=none_extractor,
        schema_path=valid_schema_path,
        meta={},
        output_dir=out_dir
    )

    with pytest.raises(TypeError, match="The extractor function must return a list of entries, got NoneType"):
        pipeline.run(data_dir)


def test_pipeline_schema_validation_failure(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    out_dir = tmp_path / "extracted"

    schema_path = tmp_path / "schema.json"
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {
            "meta": {"type": "object"},
            "entries": {
                "type": "array",
                "items": {"type": "object"}
            }
        },
        "required": ["meta", "entries"]
    }
    schema_path.write_text(json.dumps(schema), encoding='utf-8')

    def bad_extractor(path: Path) -> Any:
        return [1, 2, 3]

    pipeline = Pipeline(
        extractor_func=bad_extractor,
        schema_path=schema_path,
        meta={},
        output_dir=out_dir
    )

    with pytest.raises(jsonschema.ValidationError):
        pipeline.run(data_dir)
        
    # The atomic file should not be written
    assert not (out_dir / "source_map.json").exists()
