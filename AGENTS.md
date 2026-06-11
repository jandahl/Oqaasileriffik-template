# AGENTS.md - Instructions for AI Agents / Collaborators

## Purpose
This repository is a standardized data extraction pipeline. It is responsible for parsing upstream data sources and outputting a standardized `source_map.json` envelope for downstream consumption.

## Rules for Agents
- Always run full conversion + validation before committing `extracted/source_map.json`
- Use atomic writes (`tmp.write_text` -> `os.replace`) and schema validation in `oqaasileriffik_convert/convert.py`
- Follow commit discipline and logging rules from handover
- **Standard Source Map**: Any extracted data must be validated against `oqaasileriffik_convert/schema.json` and wrapped in the `meta` + `entries` envelope as defined in the UPSTREAM_MAP_DESIGN.
- For structural or architectural changes: present a plan before executing.

Refer to the PR history or handover notes for full spec constraints.
