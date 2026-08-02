# PHYB Site

Django site for PHYB — portfolio, blog, and order processing for the
Signpost / Starter / Pro website packages, with Paynow (Ecocash/OneMoney)
payment collection.

## Stack

- Django 5, split settings (`config/settings/{base,dev,test,prod}.py`) via `python-decouple`
- Hand-written CSS (`static/css/main.css`) and vanilla JS (`static/js/main.js`) — no frontend framework. Includes a light/dark theme toggle, persisted in `localStorage`.
- `django-htmx` for the payment-status polling widget
- `django-crispy-forms` (with the `crispy-bootstrap5` template pack purely for its form-field markup conventions — no actual Bootstrap CSS/JS is loaded anywhere)
- Paynow SDK for Ecocash/OneMoney/web checkout
- WhiteNoise for static files (no separate CDN needed on cPanel)
- pytest + pytest-django + factory_boy for tests

## Local setup (Termux or desktop)

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt

cp .env.example .env
# edit .env — at minimum set a real SECRET_KEY for anything beyond quick testing

./scripts/fetch_vendor_assets.sh   # downloads htmx into static/vendor/ — needs network, run once
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit `http://127.0.0.1:8000`. Admin is at `/admin/`.

### Debug toolbar

`django-debug-toolbar` is enabled automatically under `config.settings.dev` (SQL queries, template context, request timing). If you're testing from your phone's browser against a dev server bound to `0.0.0.0` rather than `127.0.0.1` — common on Termux — the toolbar is configured to show up regardless of the request's source IP, since the default `INTERNAL_IPS`-only check doesn't account for that setup. It's dev-only: `config.settings.prod` never imports it.

### Why htmx is vendored instead of loaded from a CDN

`htmx` is downloaded once into `static/vendor/` rather than loaded from a CDN in `base.html`, so the payment-status polling still works with no network access and the site has one less third-party runtime dependency. Re-run `scripts/fetch_vendor_assets.sh` to update the pinned version; `static/vendor/` is gitignored since it's a build artifact, not source. There is no CSS framework to vendor — `static/css/main.css` is hand-written and has zero external dependency.

### Contact details

WhatsApp number, phone, email, and address are read from `.env` (`WHATSAPP_NUMBER`, `CONTACT_PHONE_DISPLAY`, `CONTACT_EMAIL`, `BUSINESS_ADDRESS`) and exposed to every template via `apps/core/context_processors.py`. Change a phone number by editing `.env`, not by hunting through templates.

## Running tests

```bash
pytest                      # full suite
pytest apps/orders          # just one app
pytest -k "test_signpost"   # by name
pytest --cov=apps           # with coverage (needs pytest-cov)
```

Tests run against `config.settings.test` (sqlite, fast password hasher, no
real Paynow calls — the Paynow client is fully mocked in
`apps/orders/tests/test_services.py`).

## Paynow setup

1. Create a merchant account at https://www.paynow.co.zw and get your
   Integration ID + Integration Key.
2. Set `PAYNOW_INTEGRATION_ID`, `PAYNOW_INTEGRATION_KEY`, `PAYNOW_RETURN_URL`,
   `PAYNOW_RESULT_URL` in `.env` (or the real environment in prod).
3. `PAYNOW_RESULT_URL` must be a **publicly reachable** URL — Paynow's
   servers POST to it directly, so this won't work against `127.0.0.1`
   until deployed. Test the Ecocash/OneMoney flow against a real host or a
   tunnel (e.g. ngrok) pointed at `/orders/payment/update/`.

## Deploying to cPanel (Passenger)

This follows the same pattern as the Shato Sports Bar / KurudzArt deploys:

1. Upload the project, create a Python app in cPanel pointing at this
   directory — cPanel generates its own `passenger_wsgi.py`; **replace it**
   with the one in this repo, which sets
   `DJANGO_SETTINGS_MODULE=config.settings.prod`.
2. `pip install -r requirements.txt` inside the cPanel-provided virtualenv.
3. Set real environment variables in cPanel's "Setup Python App" env vars
   section — `SECRET_KEY`, `DATABASE_URL` (if using Postgres), Paynow keys,
   `ALLOWED_HOSTS`.
4. Confirm `logs/` exists in the deployed directory (it's tracked via
   `logs/.gitkeep`) — a missing `logs/` directory crashes Passenger on
   boot before Django even loads, since the file logging handler tries to
   open a file in it immediately.
5. `python manage.py migrate && python manage.py collectstatic --noinput`.
6. If serving from an addon/subdomain, double check `STATIC_URL`/media
   serving against `PassengerBaseURI`, same as the LiteSpeed/thosheck
   static file fix from earlier projects — WhiteNoise handles most of this
   automatically but subdomain-mounted addon domains have bitten before.

## Project layout

```
config/               settings (base/dev/test/prod), root urls, wsgi/asgi
apps/core/             base.html, home/about/pricing, error handlers
apps/portfolio/        past client work
apps/blog/              articles
apps/orders/            lead capture form + Paynow order processing
templates/admin/       admin branding overrides (base_site.html, index.html)
templates/errors/      404/500
static/css/main.css    global brand styles (mobile-first)
```

## Known gaps / next steps

- No pagination yet on portfolio/blog lists — fine at current content volume, revisit if either grows past ~20 items.
- `PaymentAttempt.raw_response` stores the Paynow response as a plain string for debugging; fine for a single-operator setup, but if this ever needs a real audit trail, move it to JSONField.
- No image resizing/thumbnailing on `cover_image` uploads — add `django-imagekit` or similar if upload sizes become a problem on cPanel storage.
