PYTHON=python

.PHONY: install validate validate-warn sources privacy privacy-strict xlsx html-preview html-check report missing readiness coverage ids schemas import-plan tabs-plan validation-plan formatting-plan summary inventory preflight

install:
	pip install -r requirements.txt

validate:
	$(PYTHON) scripts/tools/validate_csv_structure.py

validate-warn:
	$(PYTHON) scripts/tools/validate_csv_structure.py --warn-only

sources:
	$(PYTHON) scripts/tools/validate_workbook_sources.py

privacy:
	$(PYTHON) scripts/tools/privacy_scan.py

privacy-strict:
	$(PYTHON) scripts/tools/privacy_scan.py --strict

xlsx: sources
	$(PYTHON) scripts/tools/build_workbook_from_csv.py

html-preview:
	$(PYTHON) scripts/tools/build_html_preview.py

html-check: html-preview
	$(PYTHON) scripts/tools/validate_html_preview.py

report:
	$(PYTHON) scripts/tools/build_data_report.py

missing:
	$(PYTHON) scripts/tools/build_missing_values_report.py

readiness:
	$(PYTHON) scripts/tools/build_launch_readiness_report.py

coverage:
	$(PYTHON) scripts/tools/build_source_coverage_report.py

ids:
	$(PYTHON) scripts/tools/build_id_registry_report.py

schemas:
	$(PYTHON) scripts/tools/build_schema_report.py

import-plan:
	$(PYTHON) scripts/tools/build_import_plan.py

tabs-plan:
	$(PYTHON) scripts/tools/build_google_sheet_tabs_plan.py

validation-plan:
	$(PYTHON) scripts/tools/build_google_sheet_validation_plan.py

formatting-plan:
	$(PYTHON) scripts/tools/build_google_sheet_formatting_plan.py

summary:
	$(PYTHON) scripts/tools/build_preflight_summary.py

inventory:
	$(PYTHON) scripts/tools/list_project_files.py

preflight: validate sources privacy xlsx html-check report missing readiness coverage ids schemas import-plan tabs-plan validation-plan formatting-plan summary inventory
