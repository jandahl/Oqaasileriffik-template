import json
import os
from pathlib import Path

import pytest

from oqaasileriffik_pipeline.core import write_atomic


def test_write_atomic_success(tmp_path: Path) -> None:
    target = tmp_path / "test.json"
    data = {"key": "value"}
    
    write_atomic(target, data)
    
    assert target.exists()
    assert json.loads(target.read_text(encoding='utf-8')) == data


def test_write_atomic_creates_parents(tmp_path: Path) -> None:
    target = tmp_path / "deep" / "nested" / "test.json"
    data = {"key": "value"}
    
    write_atomic(target, data)
    
    assert target.exists()


def test_write_atomic_cleanup_on_serialization_error(tmp_path: Path) -> None:
    target = tmp_path / "test.json"
    
    class Unserializable:
        pass
        
    data = {"key": Unserializable()}
    
    with pytest.raises(TypeError):
        write_atomic(target, data)
        
    # The temporary file should be cleaned up
    tmp_files = list(tmp_path.glob(".test.json.*.tmp"))
    assert len(tmp_files) == 0
    assert not target.exists()


def test_write_atomic_propagates_oserror_cleanly(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    target = tmp_path / "test.json"
    data = {"key": "value"}
    
    # Mock os.replace to simulate an atomic move failure
    def mock_replace(src: str, dst: str) -> None:
        raise OSError(13, "Permission denied", src, 13, dst)
        
    monkeypatch.setattr(os, "replace", mock_replace)
    
    with pytest.raises(OSError) as exc_info:
        write_atomic(target, data)
        
    assert exc_info.value.errno == 13
    assert "Permission denied" in str(exc_info.value)
    
    # Verify cleanup occurred
    tmp_files = list(tmp_path.glob(".test.json.*.tmp"))
    assert len(tmp_files) == 0
