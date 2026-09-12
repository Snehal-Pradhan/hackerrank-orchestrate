FROM python:3.11-slim

WORKDIR /srv/agent

RUN python -m pip install --no-cache-dir --upgrade pip setuptools wheel

COPY pyproject.toml .
COPY core/ core/
COPY plugins/ plugins/
COPY recipes/ recipes/
COPY deploy/aws/entrypoint.py ./entrypoint.py

RUN python -m pip install --no-cache-dir ".[aws]"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

ENTRYPOINT ["python", "entrypoint.py"]
CMD ["--help"]
