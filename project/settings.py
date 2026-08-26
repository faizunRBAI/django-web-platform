"""Django settings — production-lean defaults for the UDAP EC2 blueprint."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def _env_flag(name: str, default: str = "0") -> bool:
    return os.environ.get(name, default).strip().lower() in {"1", "true", "yes", "on"}


# Never ship a usable fallback secret: production must supply DJANGO_SECRET_KEY.
# The configure stage writes it to /opt/app/.env from the pipeline secret.
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")
DEBUG = _env_flag("DJANGO_DEBUG")

if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "insecure-debug-only-key"
    else:
        raise RuntimeError(
            "DJANGO_SECRET_KEY is not set. Provide it via the environment "
            "(the deploy pipeline writes it to /opt/app/.env)."
        )

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",")
    if host.strip()
]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "project.urls"
WSGI_APPLICATION = "project.wsgi.application"

TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "core" / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": []},
}]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.environ.get("DJANGO_DB_PATH", BASE_DIR / "db.sqlite3"),
    }
}

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Behind nginx: trust the proxy's forwarded scheme header.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
