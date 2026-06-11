# Oqaasileriffik Template Repository

This is a GitHub Template Repository for bootstrapping Oqaasileriffik data extraction pipelines. 

It provides a standardized environment including:
* Python 3.10+ virtual environment bootstrapping (`scripts/bootstrap_venv.sh`)
* Linting and formatting with `ruff`
* Type checking with `mypy`
* Standardized `UPSTREAM_MAP_DESIGN` envelope validation (`convert/schema.json`)
* Standardized AI agent instructions (`AGENTS.md`)

## Getting Started

1. Clone or generate your repository from this template.
2. Run the bootstrap script to create the `.venv` and install all tools:
   ```bash
   ./scripts/bootstrap_venv.sh
   source .venv/bin/activate
   ```
3. Update `convert/convert.py` with the specific extraction logic for your upstream dataset.
4. Update `pyproject.toml` with any specific dependencies (e.g. `odfpy`, `openpyxl`).
5. Ensure your script outputs a valid `extracted/source_map.json` using the provided schema.

## License
Default license: Mozilla Public License 2.0 (MPL-2.0) + Rights Reserved.
