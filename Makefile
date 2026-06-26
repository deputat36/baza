PYTHON=python

.PHONY: install validate validate-warn privacy privacy-strict xlsx inventory preflight

install:
	pip install -r requirements.txt

validate:
	$(PYTHON) scripts/tools/validate_csv_structure.py

validate-warn:
	$(PYTHON) scripts/tools/validate_csv_structure.py --warn-only

privacy:
	$(PYTHON) scripts/tools/privacy_scan.py

privacy-strict:
	$(PYTHON) scripts/tools/privacy_scan.py --strict

xlsx:
	$(PYTHON) scripts/tools/build_workbook_from_csv.py

inventory:
	$(PYTHON) scripts/tools/list_project_files.py

preflight: validate privacy xlsx inventory
