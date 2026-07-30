#!/usr/bin/env bash
set -euo pipefail

# Deploy Psyclonic Studios to Google App Engine
# Usage: ./deploy.sh

echo "==> Exporting requirements.txt from uv.lock..."
uv export --format requirements-txt --no-dev -o requirements.txt

echo "==> Deploying to Google App Engine..."
gcloud app deploy app.yaml --project psyclonic-studios-website

echo "==> Done!"
