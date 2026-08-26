# django-web-platform — working notes

## Origin
Anchored on Marketplace blueprint `django-ec2@1.0.0` (Django Web Platform on AWS EC2).
Blueprint provided: infra/ (EC2+EIP+SG), ansible/playbook.yml, pipeline backbone,
core/ landing page + /health, project/ Django config.

## Decisions
- Region **us-east-1** (user's AWS default). Blueprint default was eu-west-1 —
  architecture.d2 header corrected to match the approved meta and the pipeline.
- Tier 1: single t3.micro + Elastic IP, default VPC, SQLite on-instance.
  No RDS/ALB/monitoring — listed as optional enhancements on the plan card.
- Ubuntu 22.04 AMI (Canonical owner 099720109477) => SSH_USER = `ubuntu`.
- nginx :80 -> gunicorn 127.0.0.1:8000 under systemd, user www-data.

## Changes I made to the blueprint
1. `project/settings.py` — removed the `change-me-in-production` fallback secret.
   SECRET_KEY now comes from env and the app REFUSES to boot without it unless
   DEBUG. Added STATIC_ROOT, SecurityMiddleware, SECURE_PROXY_SSL_HEADER,
   env-driven ALLOWED_HOSTS and DJANGO_DB_PATH.
2. `ansible/playbook.yml` — added: wait_for_connection, assert on the secret,
   apt cache refresh WITHOUT cache_valid_time (stale-index 404 pitfall),
   retries on apt, `.env` (0600) + systemd EnvironmentFile so gunicorn actually
   receives the secret, collectstatic, www-data ownership, handlers +
   flush_handlers, wait_for port, local /health probe. All modules are
   ansible.builtin (ansible-core ships no collections).
3. `.udap/pipeline.yaml` — added a `test` stage (manage.py check + test) gating
   provision; added ssh-keyscan to configure; passes DJANGO_SECRET_KEY through
   to the playbook via -e.
4. `core/tests.py` — new; covers `/health` JSON and `/` template rendering.
   The pipeline's test stage would otherwise run against zero tests.

## Gotchas
- `/health` has NO trailing slash in project/urls.py — verify curls `http://IP/health`.
  Do not add APPEND_SLASH-dependent routing there.
- SQLite file is owned by www-data; migrations run as root then ownership is fixed.
  If a deploy ever fails with "attempt to write a readonly database", check that
  the ownership task ran after migrate.
- DJANGO_SECRET_KEY is a repo secret — must be set AFTER create_repo_and_push
  and BEFORE deploy.

## Status
- [x] Meta approved, design approved, plan approved
- [x] Blueprint materialised + tailored
- [ ] validate_project / test_project
- [ ] push, secret, deploy
