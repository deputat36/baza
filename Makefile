PYTHON=python

.PHONY: install validate privacy xlsx inventory preflight

install:
	pip install -r requirements.txt

validate:
	$(PYTHON) scripts/tools/validate_csv_structure.py

privacy:
	$(PYTHON) scripts/tools/privacy_scan.py

xlsx:
	$(PYTHON) scripts/tools/build_workbook_from_csv.py

inventory:
	$(PYTHON) scripts/tools/list_project_files.py

preflight: validate privacy xlsx inventory
