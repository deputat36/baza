PYTHON=python

.PHONY: install validate validate-warn sources privacy privacy-strict xlsx report inventory preflight

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

inventory:
	$(PYTHON) scripts/tools/list_project_files.py

preflight: validate sources privacy xlsx report inventory
