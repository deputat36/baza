PYTHON=python

.PHONY: install validate validate-warn sources privacy privacy-strict xlsx report coverage ids schemas inventory preflight

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

report:
	$(PYTHON) scripts/tools/build_data_report.py

coverage:
	$(PYTHON) scripts/tools/build_source_coverage_report.py

ids:
	$(PYTHON) scripts/tools/build_id_registry_report.py

schemas:
	$(PYTHON) scripts/tools/build_schema_report.py

inventory:
	$(PYTHON) scripts/tools/list_project_files.py

preflight: validate sources privacy xlsx report coverage ids schemas inventory
