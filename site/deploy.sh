#!/bin/bash
# Deploy kompress.vaked.dev — push + clear caches
set -e

echo "=== Deploy kompress.vaked.dev ==="

# Push to GitHub
cd "$(dirname "$0")/.."
git add -A
git commit -m "deploy $(date -u +%Y-%m-%dT%H:%M:%SZ)" || true
git push origin main

echo "✓ Pushed to GitHub"

# Clear Cloudflare cache (if CF_API_TOKEN is set)
if [ -n "$CF_API_TOKEN" ] && [ -n "$CF_ZONE_ID" ]; then
  echo "Clearing Cloudflare cache..."
  curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/purge_cache" \
    -H "Authorization: Bearer $CF_API_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"purge_everything":true}' | python3 -c "import json,sys;d=json.load(sys.stdin);print('CF:',d.get('success','?'))"
fi

# Bust GitHub Pages cache (force re-fetch)
GH_URL="https://kompress.vaked.dev/?nocache=$(date +%s)"
curl -s -o /dev/null -w "HTTP %{http_code}" "$GH_URL"
echo ""

echo "✓ Deploy complete"
echo "  https://kompress.vaked.dev"
