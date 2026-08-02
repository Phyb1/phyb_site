#!/usr/bin/env bash
# Downloads a pinned htmx build into static/vendor/ so the site never
# depends on a CDN being reachable at request time. Run this once after
# cloning (needs network — fine on your device even though the sandbox
# that generated this project didn't have any).
#
# Bootstrap is NOT vendored — the project uses a hand-written stylesheet
# (static/css/main.css) and vanilla JS (static/js/main.js) instead, no
# framework dependency at all.
set -euo pipefail
cd "$(dirname "$0")/.."

mkdir -p static/vendor

curl -fsSL -o static/vendor/htmx.min.js \
  https://unpkg.com/htmx.org@1.9.12/dist/htmx.min.js

echo "htmx downloaded into static/vendor/. Run 'python manage.py collectstatic' before deploying."
