# django-web-platform

Django web platform running on a single AWS EC2 instance, built from the
**Django Web Platform on AWS EC2** production blueprint (`django-ec2@1.0.0`).

nginx terminates public traffic on port 80 and proxies to gunicorn on
`127.0.0.1:8000`, managed by systemd. Data lives in SQLite on the instance.

## Architecture

| Component | Detail |
|---|---|
| Compute | EC2 `t3.micro`, Ubuntu 22.04, Elastic IP |
| Network | Default VPC, security group open on 22 / 80 / 443 |
| Web entrypoint | nginx reverse proxy (`/static/` served directly) |
| App server | gunicorn, 2 workers, under systemd (`app.service`) |
| Database | SQLite at `/opt/app/db.sqlite3` |
| Region | `us-east-1` |

The source of truth for the architecture is [`.udap/architecture.d2`](.udap/architecture.d2).

## Routes

| Path | Purpose |
|---|---|
| `/` | Landing page (HTML) |
| `/health` | `{"status": "ok"}` — used by the deploy verify stage |

## Run locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DJANGO_SECRET_KEY=local-dev-key
export DJANGO_DEBUG=1
python manage.py migrate
python manage.py runserver
```

Then open http://127.0.0.1:8000/.

## Tests

```bash
DJANGO_SECRET_KEY=ci-key python manage.py test
```

## Configuration

Settings are read from the environment. On the server these come from
`/opt/app/.env`, written by the configure stage (mode `0600`).

| Variable | Required | Default | Notes |
|---|---|---|---|
| `DJANGO_SECRET_KEY` | yes | — | App refuses to start without it when `DEBUG` is off |
| `DJANGO_DEBUG` | no | `0` | `1`/`true` enables debug mode |
| `DJANGO_ALLOWED_HOSTS` | no | `*` | Comma-separated |
| `DJANGO_DB_PATH` | no | `BASE_DIR/db.sqlite3` | SQLite file location |

## Deploy

Deployment runs through the UDAP pipeline defined in
[`.udap/pipeline.yaml`](.udap/pipeline.yaml) — never edit the rendered
workflows in `.github/workflows/` directly.

1. **test** — `manage.py check` + `manage.py test`
2. **provision** — `terraform apply` in `infra/` (EC2, EIP, security group)
3. **configure** — Ansible installs the runtime, migrates, and starts gunicorn/nginx
4. **verify** — health checks `/health` and `/` with retries

Terraform state is stored in the platform-managed bucket; the backend block in
`infra/main.tf` is intentionally empty and configured at `init` time.

### Required repository secret

| Secret | Purpose |
|---|---|
| `DJANGO_SECRET_KEY` | Django signing key, delivered to `/opt/app/.env` |

Cloud credentials, `PROJECT_NAME`, `TF_STATE_BUCKET` and the SSH key pair are
provided by the platform automatically.

## Operate

```bash
ssh ubuntu@<elastic-ip>
sudo systemctl status app          # gunicorn service
sudo journalctl -u app -n 100      # application logs
sudo nginx -t && sudo systemctl reload nginx
```

## Scaling beyond SQLite

SQLite lives on the instance's root volume and does not survive instance
replacement. When you need durability or more than one app server, ask the
Build Agent to add RDS Postgres — the blueprint is designed for that upgrade.
