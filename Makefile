PYTHON=python

.PHONY: install validate validate-warn sources privacy privacy-strict xlsx html-preview html-check report missing readiness coverage ids schemas freshness change-requests role-navigation import-plan tabs-plan validation-plan formatting-plan knowledge-index knowledge-check relationships deal-hints deal-signals deal-hint-preview deal-audiences deal-hint-ui-map deal-hint-api-examples integration-json-fields integration-visibility integration-access integration-contracts manager-dashboard summary artifact-index inventory preflight

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

freshness:
	$(PYTHON) scripts/tools/build_data_freshness_report.py

change-requests:
	$(PYTHON) scripts/tools/build_change_request_report.py

role-navigation:
	$(PYTHON) scripts/tools/build_role_navigation_report.py

import-plan:
	$(PYTHON) scripts/tools/build_import_plan.py

tabs-plan:
	$(PYTHON) scripts/tools/build_google_sheet_tabs_plan.py

validation-plan:
	$(PYTHON) scripts/tools/build_google_sheet_validation_plan.py

formatting-plan:
	$(PYTHON) scripts/tools/build_google_sheet_formatting_plan.py

knowledge-index:
	$(PYTHON) scripts/tools/build_knowledge_index.py

knowledge-check: knowledge-index
	$(PYTHON) scripts/tools/validate_knowledge_index.py

relationships: knowledge-check
	$(PYTHON) scripts/tools/build_relationship_report.py

deal-hints: knowledge-check
	$(PYTHON) scripts/tools/build_deal_hint_rules.py

deal-signals:
	$(PYTHON) scripts/tools/build_deal_signal_report.py

deal-hint-preview: deal-hints
	$(PYTHON) scripts/tools/build_deal_hint_preview.py

deal-audiences:
	$(PYTHON) scripts/tools/build_deal_audience_report.py

deal-hint-ui-map: deal-hints
	$(PYTHON) scripts/tools/build_deal_hint_ui_map.py

deal-hint-api-examples: deal-hint-preview
	$(PYTHON) scripts/tools/build_deal_hint_api_examples.py

integration-json-fields: deal-hint-api-examples
	$(PYTHON) scripts/tools/validate_integration_json_fields.py

integration-visibility:
	$(PYTHON) scripts/tools/build_integration_data_visibility_report.py

integration-access:
	$(PYTHON) scripts/tools/build_integration_access_report.py

integration-contracts:
	$(PYTHON) scripts/tools/build_integration_contract_report.py

manager-dashboard: readiness freshness change-requests missing integration-access integration-contracts
	$(PYTHON) scripts/tools/build_manager_dashboard.py

summary:
	$(PYTHON) scripts/tools/build_preflight_summary.py

artifact-index:
	$(PYTHON) scripts/tools/build_artifact_index.py

inventory:
	$(PYTHON) scripts/tools/list_project_files.py

preflight: validate sources privacy xlsx html-check report missing readiness coverage ids schemas freshness change-requests role-navigation import-plan tabs-plan validation-plan formatting-plan relationships deal-hints deal-signals deal-hint-preview deal-audiences deal-hint-ui-map deal-hint-api-examples integration-json-fields integration-visibility integration-access integration-contracts manager-dashboard summary artifact-index inventory
