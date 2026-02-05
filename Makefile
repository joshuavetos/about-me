install:
	pip install -r requirements.txt

test:
	pytest test_pipeline.py

run:
	python -c "from audit_pipeline import run_financial_audit; print(run_financial_audit([{'project_name': 'Test', 'budget_allocation': 1000.0, 'fiscal_start': 2025, 'fiscal_end': 2026}]))"
