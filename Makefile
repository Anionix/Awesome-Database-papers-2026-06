PYTHON ?= python3
PSQL ?= psql

.PHONY: check generate sql-check explain-check

check:
	$(PYTHON) scripts/validate_catalog.py
	$(PYTHON) scripts/generate_catalog.py --check
	$(PYTHON) scripts/check_sql.py

generate:
	$(PYTHON) scripts/generate_catalog.py

sql-check:
	$(PYTHON) scripts/check_sql.py
	@if [ -n "$$DATABASE_URL" ]; then \
		$(PSQL) "$$DATABASE_URL" -v ON_ERROR_STOP=1 -f docs/repo-db-schema.sql -f examples/seed.sql -f examples/queries.sql -f examples/explain.sql; \
	else \
		echo "DATABASE_URL not set; skipped live psql execution after static SQL checks."; \
	fi

explain-check:
	@if [ -z "$$DATABASE_URL" ]; then \
		echo "DATABASE_URL must point to an empty scratch PostgreSQL database."; \
		exit 1; \
	fi
	$(PSQL) "$$DATABASE_URL" -v ON_ERROR_STOP=1 -f docs/repo-db-schema.sql -f examples/seed.sql -f examples/explain.sql
