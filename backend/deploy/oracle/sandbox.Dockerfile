FROM python:3.13-slim-bookworm

RUN apt-get update \
    && apt-get install --no-install-recommends -y g++ \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /workspace
