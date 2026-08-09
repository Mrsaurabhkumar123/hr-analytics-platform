#!/usr/bin/env sh
set -e

echo "Waiting for MySQL at ${DB_HOST:-mysql}:${DB_PORT:-3306}..."
python - <<'PY'
import os, time, sys
import pymysql

host = os.environ.get("DB_HOST", "mysql")
port = int(os.environ.get("DB_PORT", 3306))
user = os.environ.get("DB_USER", "hr_app")
password = os.environ.get("DB_PASSWORD", "hr_app_password")

for attempt in range(30):
    try:
        conn = pymysql.connect(host=host, port=port, user=user, password=password, connect_timeout=3)
        conn.close()
        print("MySQL is ready.")
        sys.exit(0)
    except Exception as exc:
        print(f"  ...not ready yet ({attempt + 1}/30): {exc}")
        time.sleep(2)
print("MySQL did not become ready in time.", file=sys.stderr)
sys.exit(1)
PY

echo "Seeding database (skipped automatically if already populated)..."
python -m app.seed --reset

echo "Training attrition-risk model..."
python -m app.ml.train_model || echo "Model training skipped/failed - API will report model_not_trained until retried."

echo "Starting Gunicorn..."
exec gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 wsgi:app
