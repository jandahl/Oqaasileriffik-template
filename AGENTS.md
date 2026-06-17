# AGENTS.md - Instructions for AI Agents / Collaborators

## Purpose
This repository is a standardized data extraction pipeline. It is responsible for parsing upstream data sources and outputting a standardized `source_map.json` envelope for downstream consumption.

## Rules for Agents
- Always run full conversion + validation before committing `extracted/source_map.json`
- Use atomic writes (`tmp.write_text` -> `os.replace`) and schema validation in `example_extractor/example_extractor.py`
- Follow commit discipline and logging rules from handover
- **Standard Source Map**: Any extracted data must be validated against `example_extractor/schema.json` and wrapped in the `meta` + `entries` envelope as defined in the UPSTREAM_MAP_DESIGN.
- For structural or architectural changes: present a plan before executing.

## Architecture and Python Packaging Lessons
- **`__init__.py` Required:** Any directory listed in `tool.setuptools.packages` must contain an `__init__.py` file (even if empty/docstring only) to ensure `setuptools` packages it properly and includes `package-data`.
- **Pre-flight Checks:** Validate the existence of `schema.json` using `path.is_file()` *before* invoking `Pipeline(...)`. This prevents the pipeline from raising generic `ValueError`s during initialization and allows for clean `FileNotFoundError`s.
- **Exception Logging:** When adding fallback `except Exception` blocks, always use `log.exception(...)` instead of `log.error(...)` to preserve the stack trace. However, you should also specifically catch `jsonschema.ValidationError` to suppress redundant tracebacks since `Pipeline.run()` logs schema violations gracefully.
- **CLI Testability:** Construct `main()` and underlying implementation functions to accept an optional `argv: list[str] | None = None` argument so they can be unit-tested without mocking `sys.argv`. Have `main()` return an integer exit code rather than calling `sys.exit()` directly, reserving the `sys.exit()` call exclusively for the `if __name__ == "__main__":` execution block.

Refer to the PR history or handover notes for full spec constraints.
