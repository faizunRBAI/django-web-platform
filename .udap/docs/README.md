# Django Web Platform on AWS EC2

A Django application served by gunicorn behind nginx on a dedicated Ubuntu EC2 instance, with migrations run on every deploy.

## What you inherit

- EC2 + Elastic IP + security group as Terraform under `infra/`
- Ansible configuration: venv, gunicorn systemd unit, nginx, `migrate` on deploy
- Health-checked verify stage

## What the Build Agent tailors

- Your Django apps under `core/`
- Instance size, region
- Database upgrades (SQLite → RDS) via the Build Agent

## Deploy behaviour

The pipeline provisions infrastructure with Terraform (state lives in the
platform-managed bucket, keyed by project), configures the server, and verifies
`/health` before the run goes green. Destroy tears down everything the template
created — the repository and its configuration survive for redeploys.
